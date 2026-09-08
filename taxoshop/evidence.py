"""Snapshot GitHub evidence and retain diagnostic text without model rewriting."""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .artifacts import content_hash, digest, encode, now, read_json, write, write_json
from .contracts import validate_schema

ISSUE = re.compile(r'https://github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)/issues/(?P<number>\d+)(?:[/?#].*)?$')
FIX = re.compile(r'https://github\.com/[\w.-]+/[\w.-]+/(?:pull/\d+|commit/[a-fA-F0-9]{7,40})')
ATTACHMENT = re.compile(r'https://(?:github\.com/(?:user-attachments|[\w.-]+/[\w.-]+/files)/[^\s<>"\)]+|(?:user-images|gist|raw)\.githubusercontent\.com/[^\s<>"\)]+)')
SANITIZER = re.compile(r'AddressSanitizer|UndefinedBehaviorSanitizer|MemorySanitizer|ThreadSanitizer|LeakSanitizer|Valgrind|Memcheck|HEAP SUMMARY:|\bruntime error:', re.I)
DIAGNOSTIC = re.compile(r'(?im)(?:ERROR|WARNING|SUMMARY):\s*(?:Address|UndefinedBehavior|Memory|Thread|Leak)Sanitizer|\bruntime error:|^==\d+==\s+(?:Memcheck|HEAP SUMMARY:|LEAK SUMMARY:|ERROR SUMMARY:|Invalid (?:read|write|free)|.*bytes in .*blocks)')
TRUNCATED = re.compile(r'(?im)^\s*(?:\.\.\.|…|\[.*(?:truncated|omitted).*\])\s*$|output truncated', re.I)
SAFE_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,120}$')


def parse_issue(url):
    match = ISSUE.fullmatch(url)
    if not match:
        raise ValueError(f'Unsupported GitHub issue URL: {url}')
    return match['owner'], match['repo'], int(match['number'])


def issue_url(url):
    owner, repo, number = parse_issue(url)
    return f'https://github.com/{owner.lower()}/{repo.lower()}/issues/{number}'


def load_corpus(path):
    path = Path(path)
    if path.suffix == '.json':
        data = read_json(path)
        validate_schema(data, 'corpus')
        bugs = data['bugs']
    else:
        urls = list(dict.fromkeys(issue_url(line.strip()) for line in path.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')))
        bugs = [{'defect_id': '-'.join(map(str, parse_issue(url))), 'issues': [url]} for url in urls]
    if not bugs:
        raise ValueError('Corpus is empty')
    seen = set()
    for bug in bugs:
        identifier = bug['defect_id']
        if not SAFE_ID.fullmatch(identifier) or identifier in seen:
            raise ValueError(f'Invalid or duplicate canonical defect ID: {identifier}')
        seen.add(identifier)
        bug['issues'] = list(dict.fromkeys(issue_url(url) for url in bug['issues']))
        if not bug['issues']:
            raise ValueError('Each defect needs at least one issue URL')
        for log in bug.get('sanitizer_logs', []):
            log['path'] = str((path.parent / log['path']).resolve())
        if bug.get('sanitizer_applicability', 'unknown') not in ('required', 'unknown', 'not_applicable'):
            raise ValueError('Invalid sanitizer applicability')
        if bug.get('sanitizer_applicability') == 'not_applicable' and not bug.get('sanitizer_rationale'):
            raise ValueError('Non-applicable sanitizer evidence requires a rationale')
    return {'bugs': bugs}


class NoCredentialRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None:
            redirected.remove_header('Authorization')
            if urlparse(newurl).scheme != 'https':
                raise ValueError('Refusing non-HTTPS evidence redirect')
        return redirected


class GitHubClient:
    def __init__(self, token=None, timeout=30, max_bytes=20_000_000):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.opener = build_opener(NoCredentialRedirect())

    def get(self, url, accept='application/vnd.github+json'):
        parsed = urlparse(url)
        if parsed.scheme != 'https' or parsed.hostname not in {'api.github.com', 'github.com', 'raw.githubusercontent.com', 'gist.githubusercontent.com', 'user-images.githubusercontent.com'}:
            raise ValueError(f'Unsupported evidence host: {url}')
        headers = {'Accept': accept, 'User-Agent': 'taxoshop-research/0.1', 'X-GitHub-Api-Version': '2022-11-28'}
        if self.token and parsed.hostname == 'api.github.com':
            headers['Authorization'] = 'Bearer ' + self.token
        for attempt in range(3):
            try:
                with self.opener.open(Request(url, headers=headers), timeout=self.timeout) as response:
                    raw = response.read(self.max_bytes + 1)
                    if len(raw) > self.max_bytes:
                        raise ValueError(f'Evidence exceeds {self.max_bytes} bytes; not silently truncated: {url}')
                    return raw, dict(response.headers)
            except HTTPError as error:
                if error.code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(min(5, 2 ** attempt))
                    continue
                raise RuntimeError(f'GitHub HTTP {error.code}: {url}') from error
            except URLError as error:
                raise RuntimeError(f'Could not fetch {url}: {error.reason}') from error
        raise AssertionError('unreachable')

    def json(self, url):
        raw, _ = self.get(url)
        return json.loads(raw)

    def pages(self, url):
        records = []
        seen = set()
        while url:
            if url in seen:
                raise ValueError('Pagination loop')
            seen.add(url)
            raw, headers = self.get(url)
            page = json.loads(raw)
            if not isinstance(page, list):
                raise ValueError('Expected a paginated array')
            records.extend(page)
            link = next((v for k, v in headers.items() if k.lower() == 'link'), '')
            match = re.search(r'<([^>]+)>;\s*rel="next"', link)
            url = match[1] if match else None
        return records


def diagnostic_blocks(text):
    """Extract exact fenced payloads; retain whole text when diagnostics occur outside fences."""
    blocks, covered = [], []
    lines = text.splitlines(keepends=True)
    offset, opening, start = 0, None, 0
    for line in lines:
        if opening is None:
            match = re.match(r' {0,3}(`{3,}|~{3,})[^\r\n]*[\r\n]*$', line)
            if match:
                opening = match[1]
                start = offset + len(line)
        elif re.fullmatch(r' {0,3}' + re.escape(opening[0]) + '{' + str(len(opening)) + r',}\s*', line):
            payload = text[start:offset]
            if DIAGNOSTIC.search(payload):
                blocks.append(payload)
                covered.append((start, offset))
            opening = None
        offset += len(line)
    if opening is not None:
        payload = text[start:]
        if DIAGNOSTIC.search(payload):
            blocks.append(payload)
            covered.append((start, len(text)))
    outside = any(not any(a <= m.start() < b for a, b in covered) for m in DIAGNOSTIC.finditer(text))
    if outside:
        return [text]  # No guessed boundary may remove diagnostic lines.
    return blocks


class Collector:
    def __init__(self, root, identifier):
        self.root = Path(root)
        self.identifier = identifier
        self.documents = []
        self.warnings = []
        self.issues = []

    def add(self, kind, origin, text, revision=None, locator='entire artifact', completeness=None, sanitizer=None, diagnostics=False):
        raw = text if isinstance(text, bytes) else text.encode('utf-8')
        identifier = f'e{len(self.documents) + 1:04d}'
        relative = f'evidence/{self.identifier}/{identifier}.txt'
        write(self.root / relative, raw)
        try:
            decoded = raw.decode('utf-8')
        except UnicodeDecodeError:
            self.warnings.append(f'Non-UTF-8 artifact retained but unavailable for text analysis: {origin}')
            decoded = ''
        item = {'id': identifier, 'kind': kind, 'origin': origin, 'artifact_path': relative,
                'sha256': digest(raw), 'retrieved_at': now(), 'revision': revision, 'locator': locator}
        doc = {'evidence': item, 'text': decoded, 'completeness': completeness, 'sanitizer': sanitizer,
               'diagnostics': diagnostics or kind in ('issue', 'comment', 'execution_log') or completeness is not None}
        self.documents.append(doc)
        return doc

    def optional(self, label, operation):
        try:
            return operation()
        except (RuntimeError, ValueError, OSError, KeyError) as error:
            self.warnings.append(f'{label}: {error}')
            return None

    def snapshot(self, bug):
        outputs = []
        for doc in self.documents:
            if not doc['diagnostics']:
                continue
            text = doc['text']
            if doc['completeness'] is not None:
                blocks = [text] if text else []
            else:
                blocks = diagnostic_blocks(text)
            for raw in blocks:
                match = SANITIZER.search(raw)
                completeness = doc['completeness'] or ('truncated' if TRUNCATED.search(raw) else 'unknown')
                if completeness not in ('full', 'truncated', 'unknown'):
                    raise ValueError('Invalid sanitizer completeness')
                if completeness == 'full' and TRUNCATED.search(raw):
                    raise ValueError('Declared full sanitizer log contains truncation markers')
                outputs.append({'id': f'log-{len(outputs) + 1:04d}', 'sanitizer': doc['sanitizer'] or (match[0] if match else 'unknown'),
                                'origin': 'reproduced' if doc['evidence']['kind'] == 'execution_log' else 'reported',
                                'completeness': completeness, 'raw_output': raw, 'raw_output_sha256': digest(raw),
                                'evidence_refs': [doc['evidence']['id']]})
        if outputs:
            status = 'complete' if all(o['completeness'] == 'full' for o in outputs) and not self.warnings else 'partial'
            reason = 'Verbatim diagnostics retained. Automatically extracted completeness is unknown unless explicitly attested in the corpus/evidence manifest.'
        elif bug.get('sanitizer_applicability') == 'not_applicable':
            status, reason = 'not_applicable', bug['sanitizer_rationale']
        else:
            status, reason = 'unavailable', 'No sanitizer output was obtained. Missing output does not establish non-applicability.'
        return {'defect_id': self.identifier, 'issues': self.issues, 'documents': self.documents,
                'reproducer_candidates': [d['evidence']['id'] for d in self.documents if d['evidence']['locator'].startswith('reproducer candidate')],
                'warnings': self.warnings, 'sanitizer_output': {'status': status, 'rationale': reason, 'outputs': outputs}}


def collect(bug, root, client=None, evidence_dir=None, max_files=30, max_fixes=10):
    collector = Collector(root, bug['defect_id'])
    if evidence_dir is not None:
        imported = read_json(Path(evidence_dir) / f'{bug["defect_id"]}.json')
        validate_schema(imported, 'evidence-bundle')
        collector.issues = imported['issues']
        if {issue_url(i['url']) for i in collector.issues} != set(bug['issues']):
            raise ValueError('Offline evidence issue URLs differ from corpus')
        for doc in imported['documents']:
            collector.add(doc['kind'], doc['origin'], doc['text'], doc.get('revision'), doc.get('locator', 'entire imported artifact'), doc.get('completeness'), doc.get('sanitizer'), doc.get('diagnostics', False))
        collector.warnings.extend(imported.get('warnings', []))
    else:
        client = client or GitHubClient()
        references = list(bug.get('fixes', []))
        source_requests = list(bug.get('source_files', []))
        for url in bug['issues']:
            owner, repo, number = parse_issue(url)
            endpoint = f'https://api.github.com/repos/{owner}/{repo}/issues/{number}'
            issue = client.json(endpoint)
            if 'pull_request' in issue:
                raise ValueError(f'Expected a bug issue, received a pull request: {url}')
            collector.issues.append({'url': url, 'state': issue.get('state', 'unknown'), 'title': issue['title']})
            collector.add('other', endpoint, encode(issue), locator='GitHub issue API payload')
            collector.add('issue', url, issue.get('body') or '', locator='issue body')
            comments = client.pages(endpoint + '/comments?per_page=100') if issue.get('comments') else []
            collector.add('other', endpoint + '/comments', encode(comments), locator='all comment API payloads')
            for comment in comments:
                collector.add('comment', comment['html_url'], comment.get('body') or '', locator=f'comment {comment["id"]}')
            timeline = collector.optional('Issue timeline', lambda: client.pages(endpoint + '/timeline?per_page=100'))
            if timeline is not None:
                collector.add('other', endpoint + '/timeline', encode(timeline), locator='GitHub timeline payload')
                for event in timeline:
                    source = event.get('source', {}).get('issue', {})
                    if source.get('pull_request') and source.get('html_url'):
                        references.append(source['html_url'])
        narrative = [d for d in collector.documents if d['evidence']['kind'] in ('issue', 'comment')]
        for doc in narrative:
            references.extend(FIX.findall(doc['text']))
            for attachment in dict.fromkeys(ATTACHMENT.findall(doc['text'])):
                def fetch_attachment(url=attachment):
                    raw, _ = client.get(url, 'text/plain')
                    collector.add('other', url, raw, locator='entire linked attachment', diagnostics=True)
                collector.optional('Linked attachment', fetch_attachment)
        references = list(dict.fromkeys(references))
        if len(references) > max_fixes:
            collector.warnings.append(f'Fix-candidate limit {max_fixes}; omitted: {references[max_fixes:]}')
        for url in references[:max_fixes]:
            def fetch_fix(url=url):
                if not FIX.fullmatch(url):
                    raise ValueError(f'Unsupported fix URL: {url}')
                parts = urlparse(url).path.strip('/').split('/')
                owner, repo, kind, ident = parts
                base = f'https://api.github.com/repos/{owner}/{repo}'
                if kind == 'pull':
                    pr = client.json(base + '/pulls/' + ident)
                    collector.add('other', url, encode(pr), locator='PR metadata; linkage is a candidate, not proof of a fix')
                    comments = client.pages(base + '/issues/' + ident + '/comments?per_page=100')
                    collector.add('other', url + '#comments', encode(comments), locator='PR discussion')
                    for comment in comments:
                        collector.add('comment', comment['html_url'], comment.get('body') or '', locator=f'PR comment {comment["id"]}')
                    for suffix in ('reviews', 'comments'):
                        reviews = collector.optional('PR ' + suffix, lambda suffix=suffix: client.pages(base + '/pulls/' + parts[-1] + '/' + suffix + '?per_page=100'))
                        if reviews is not None:
                            collector.add('other', url + '#' + suffix, encode(reviews), locator='PR review evidence')
                    if not pr.get('merged') or not pr.get('merge_commit_sha'):
                        collector.warnings.append(f'Unmerged PR: {url}; no fixed revision asserted')
                        return
                    ident = pr['merge_commit_sha']
                commit = client.json(base + '/commits/' + ident)
                sha = commit['sha']
                collector.add('other', url, encode(commit), revision=sha, locator='commit metadata and file inventory')
                raw, _ = client.get(base + '/commits/' + sha, 'application/vnd.github.diff')
                collector.add('patch', url, raw, revision=sha, locator='full commit diff')
                files = commit.get('files', [])
                if len(files) > max_files:
                    collector.warnings.append(f'Changed-source limit {max_files} for {sha}; full diff retained')
                parents = commit.get('parents', [])
                for file in files[:max_files]:
                    if parents and file.get('status') != 'added':
                        source_requests.append({'owner': owner, 'repo': repo, 'revision': parents[0]['sha'], 'path': file.get('previous_filename', file['filename'])})
                    if file.get('status') != 'removed':
                        source_requests.append({'owner': owner, 'repo': repo, 'revision': sha, 'path': file['filename']})
            collector.optional('Fix candidate', fetch_fix)
        default_owner, default_repo, _ = parse_issue(bug['issues'][0])
        seen_sources = set()
        for source in source_requests:
            owner, repo = source.get('owner', default_owner), source.get('repo', default_repo)
            sha, path = source['revision'], source['path']
            if not re.fullmatch(r'[0-9a-fA-F]{40}', sha):
                raise ValueError('Explicit source revisions must be full commit SHAs')
            url = f'https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{quote(path, safe="/")}'
            if url in seen_sources:
                continue
            seen_sources.add(url)
            def fetch_source(url=url, sha=sha, path=path):
                raw, _ = client.get(url, 'text/plain')
                collector.add('test' if '/test' in path.lower() else 'source', url, raw, revision=sha,
                              locator=f'{path}; lines 1-{len(raw.splitlines())}')
            collector.optional('Source file', fetch_source)
    for log in bug.get('sanitizer_logs', []):
        raw = Path(log['path']).read_bytes()
        collector.add('execution_log' if log.get('origin') == 'reproduced' else 'other', log.get('source_url', log['path']), raw,
                      log.get('revision'), log.get('locator', 'entire supplied sanitizer log'), log.get('completeness', 'unknown'), log.get('sanitizer'))
    for doc in list(collector.documents):
        if doc['evidence']['kind'] in ('issue', 'comment'):
            pattern = r'(?m)^ {0,3}(`{3,}|~{3,})(python|py|c|cpp|c\+\+)[ \t]*\r?\n([\s\S]*?)^ {0,3}\1[ \t]*(?:\r?\n|$)'
            for index, match in enumerate(re.finditer(pattern, doc['text']), 1):
                collector.add('other', doc['evidence']['origin'], match[3], locator=f'reproducer candidate {index} ({match[2]}) from {doc["evidence"]["id"]}; unexecuted, may be illustrative code')
    bundle = collector.snapshot(bug)
    write_json(Path(root) / 'bundles' / f'{bug["defect_id"]}.json', bundle)
    return bundle

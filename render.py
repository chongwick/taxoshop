"""Render uniformly structured bug instance reports with full verbatim issue content."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / 'taxos' / 'micro_taxo' / 'sources'
FIXES = ROOT / 'taxos' / 'micro_taxo' / 'sources' / 'fixes'
OUTPUT = ROOT / 'taxos' / 'micro_taxo'
NUMBERS = re.findall(r'/issues/(\d+)', (ROOT / 'taxos' / 'bugs.txt').read_text())
DIAGNOSTIC = re.compile(
    r'(?:Address|Leak|Memory|Thread|UndefinedBehavior)Sanitizer'
    r'|runtime error:'
    r'|==\d+=='
    r'|Invalid (?:read|write|free)'
    r'|HEAP SUMMARY'
    r'|ERROR SUMMARY',
    re.I,
)
LINKED_PRS = re.compile(r'<!-- gh-linked-prs -->(.*?)<!-- /gh-linked-prs -->', re.S)
GH_PR_REF = re.compile(r'\bgh-(\d+)\b')
PR_URL = re.compile(r'https://github\.com/python/cpython/pull/(\d+)')
COMMIT_URL = re.compile(r'https://github\.com/python/cpython/commit/([0-9a-f]{7,40})')
HG_CHANGESET = re.compile(r'^New changeset ([0-9a-f]+) by .+ in branch .+', re.M)
FIXED_BY = re.compile(r'Fixed by[:\s]+(https?://\S+)', re.I)


def fence(s, lang='text'):
    n = max([3] + [len(x) + 1 for x in re.findall(r'`+', s)])
    f = '`' * n
    return f + lang + '\n' + s + ('' if s.endswith('\n') else '\n') + f + '\n'


def extract_fix_refs(objects):
    issue_body = objects[0].get('body') or ''
    linked_prs = []
    m = LINKED_PRS.search(issue_body)
    if m:
        linked_prs = GH_PR_REF.findall(m.group(1))

    fix_prs = list(dict.fromkeys(
        pr for obj in objects
        for pr in PR_URL.findall(obj.get('body') or '')
    ))
    fix_commits = list(dict.fromkeys(
        sha for obj in objects
        for sha in COMMIT_URL.findall(obj.get('body') or '')
    ))
    changesets = list(dict.fromkeys(
        cs for obj in objects
        for cs in HG_CHANGESET.findall(obj.get('body') or '')
    ))
    fixed_by_urls = list(dict.fromkeys(
        url.rstrip('.,;)') for obj in objects
        for url in FIXED_BY.findall(obj.get('body') or '')
    ))
    return linked_prs, fix_prs, fix_commits, changesets, fixed_by_urls


def render_pr(number):
    """Return rendered fix data section for a PR, or None if not collected."""
    path = FIXES / f'pr_{number}.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    pr = data['pr']
    files = data['files']
    review_comments = data['review_comments']
    issue_comments = data['issue_comments']

    out = f'### PR #{number}: {pr["title"]}\n\n'
    out += f'- URL: [{pr["html_url"]}]({pr["html_url"]})\n'
    out += f'- State: {pr["state"]}'
    if pr.get('merged_at'):
        out += f'; merged: {pr["merged_at"]}'
        if pr.get('merge_commit_sha'):
            sha = pr['merge_commit_sha']
            out += f'; merge commit: [`{sha[:12]}`](https://github.com/python/cpython/commit/{sha})'
    elif pr.get('closed_at'):
        out += f'; closed (not merged): {pr["closed_at"]}'
    out += '\n'
    out += f'- Author: {pr["user"]["login"]}\n'
    out += f'- Changes: +{pr["additions"]} / -{pr["deletions"]} across {pr["changed_files"]} file(s)\n'

    if pr.get('body'):
        out += '\n#### Description\n\n'
        out += fence(pr['body']) + '\n'

    if files:
        out += '#### Changed Files\n\n'
        for f in files:
            status = f.get('status', '')
            out += f'##### `{f["filename"]}` ({status}; +{f["additions"]} / -{f["deletions"]})\n\n'
            patch = f.get('patch')
            if patch:
                out += fence(patch, 'diff') + '\n'
            else:
                out += 'No patch available (binary or too large).\n\n'

    by_file = {}
    for c in review_comments:
        by_file.setdefault(c['path'], []).append(c)
    if by_file:
        out += '#### Review Comments\n\n'
        for filepath, comments in sorted(by_file.items()):
            out += f'##### `{filepath}`\n\n'
            for c in comments:
                out += f'**{c["user"]["login"]}**, {c["created_at"]}:\n\n'
                if c.get('diff_hunk'):
                    out += fence(c['diff_hunk'], 'diff') + '\n'
                out += fence(c['body']) + '\n'

    if issue_comments:
        out += '#### PR Discussion\n\n'
        for c in issue_comments:
            out += f'**{c["user"]["login"]}**, {c["created_at"]}:\n\n'
            out += fence(c['body']) + '\n'

    return out


def render_commit(sha):
    """Return rendered fix data section for a standalone commit, or None if not collected."""
    path = FIXES / f'commit_{sha}.json'
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    commit = data.get('commit', {})
    files = data.get('files', [])

    short = sha[:12]
    url = f'https://github.com/python/cpython/commit/{sha}'
    out = f'### Commit [`{short}`]({url})\n\n'
    out += f'- Author: {commit.get("author", {}).get("name", "unknown")}, {commit.get("author", {}).get("date", "")}\n'
    msg = (commit.get('message') or '').strip()
    if msg:
        out += '\n#### Commit Message\n\n'
        out += fence(msg) + '\n'

    if files:
        out += '#### Changed Files\n\n'
        for f in files:
            status = f.get('status', '')
            out += f'##### `{f["filename"]}` ({status}; +{f["additions"]} / -{f["deletions"]})\n\n'
            patch = f.get('patch')
            if patch:
                out += fence(patch, 'diff') + '\n'
            else:
                out += 'No patch available (binary or too large).\n\n'

    return out


def render():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    attachment_path = SOURCES / 'attachments' / 'manifest.json'
    attachments = json.loads(attachment_path.read_text()) if attachment_path.exists() else []
    manifest = []

    for n in NUMBERS:
        src = SOURCES / f'gh_{n}.json'
        if not src.exists():
            print('MISSING', n)
            continue

        d = json.loads(src.read_text())
        i = d['issue']
        objects = [i, *d['comments']]
        labels = ', '.join(x['name'] for x in i.get('labels', []))

        out = f'# CPython #{n}: {i["title"]}\n\n'
        out += '## Metadata\n\n'
        out += f'- Issue: [{i["title"]}]({i["html_url"]})\n'
        out += f'- Created: {i["created_at"]}\n'
        out += f'- Updated: {i["updated_at"]}\n'
        out += f'- Retrieved: {d["retrieved_at"]}\n'
        out += f'- Status: {i["state"]}; closed: {i.get("closed_at") or "not closed"}\n'
        out += f'- Labels: {labels or "none"}\n'
        out += f'- Comments: {len(d["comments"])}\n\n'

        linked_prs, fix_prs, fix_commits, changesets, fixed_by_urls = extract_fix_refs(objects)
        has_fix = any([linked_prs, fix_prs, fix_commits, changesets, fixed_by_urls])

        all_pr_numbers = list(dict.fromkeys(linked_prs + fix_prs))
        pr_merge_shas = set()
        for p in all_pr_numbers:
            ppath = FIXES / f'pr_{p}.json'
            if ppath.exists():
                pdata = json.loads(ppath.read_text())
                sha = pdata['pr'].get('merge_commit_sha') or ''
                if sha:
                    pr_merge_shas.add(sha)
        standalone_commits = [sha for sha in fix_commits if sha not in pr_merge_shas]

        out += '## Fix Data\n\n'
        fix_sections = []
        for p in all_pr_numbers:
            s = render_pr(p)
            if s:
                fix_sections.append(s)
        for sha in standalone_commits:
            s = render_commit(sha)
            if s:
                fix_sections.append(s)

        if fix_sections:
            out += '\n'.join(fix_sections)
        elif changesets:
            out += 'Mercurial changesets (pre-GitHub era; patch data not fetched): '
            out += ', '.join(f'`{cs}`' for cs in changesets) + '\n\n'
        elif has_fix:
            out += 'Fix references exist but fix data has not been collected yet. Run `collect_fixes.py`.\n\n'
        else:
            out += 'No fix references found in the issue or comments.\n\n'

        out += '## Source Records\n\n'
        out += 'Complete verbatim content of the issue body and every comment. '
        out += 'Sanitizer stacks, shadow bytes, allocation/free histories, and reproducers are preserved exactly as posted.\n\n'

        count = 0
        for k, obj in enumerate(objects):
            text = obj.get('body') or ''
            if k == 0:
                heading = 'Original Issue'
            else:
                heading = f'Comment {k} — {obj["user"]["login"]}, {obj["created_at"]}'
            out += f'### {heading}\n\n'
            out += f'Source: [{obj["html_url"]}]({obj["html_url"]})\n\n'
            out += fence(text) + '\n'
            if DIAGNOSTIC.search(text):
                count += 1

        related = [a for a in attachments if any(o['html_url'] in a['references'] for o in objects)]
        if related:
            out += '## Linked Text Attachments\n\n'
            for a in related:
                out += f'### [{a["path"]}]({a["url"]})\n\n'
                if a['success']:
                    raw = (SOURCES / 'attachments' / a['path']).read_bytes()
                    try:
                        text = raw.decode('utf-8')
                    except UnicodeDecodeError:
                        out += 'Binary attachment; not UTF-8 text.\n\n'
                    else:
                        out += fence(text) + '\n'
                    out += f'Local copy: [original attachment](sources/attachments/{a["path"]}); SHA-256: `{a["sha256"]}`.\n\n'
                else:
                    out += 'Retrieval failed: ' + a.get('error', 'unknown error').strip() + '\n\n'

        if count == 0:
            out += '## Sanitizer Output Availability\n\n'
            out += 'No sanitizer diagnostic marker found in the issue body or comments.\n'

        (OUTPUT / f'gh_{n}.md').write_bytes(out.encode('utf-8'))

        encoded = out.encode('utf-8')
        assert all((o.get('body') or '').encode('utf-8') in encoded for o in objects), \
            f'Source body not found verbatim in output for #{n}'

        manifest.append({
            'number': int(n),
            'title': i['title'],
            'comments': len(d['comments']),
            'diagnostic_source_records': count,
            'has_fix_references': has_fix,
            'fix_data_collected': bool(fix_sections),
            'attachments': len(related),
            'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
        })

    (OUTPUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')

    index = '# CPython bug instance reports\n\n'
    index += f'{len(manifest)} reports. Each file contains the full issue body and all comments verbatim.\n\n'
    index += '| Issue | Title | Sanitizer records | Fix data |\n|---|---|---|---|\n'
    for r in manifest:
        title = r['title'].replace('|', '\\|').replace('\n', ' ')
        fix = 'Yes' if r['fix_data_collected'] else ('Refs only' if r['has_fix_references'] else '—')
        index += f'| [#{r["number"]}](gh_{r["number"]}.md) | {title} | {r["diagnostic_source_records"]} | {fix} |\n'
    (OUTPUT / 'index.md').write_text(index)

    total_diag = sum(r['diagnostic_source_records'] for r in manifest)
    total_fix = sum(r['fix_data_collected'] for r in manifest)
    print(f'{len(manifest)} reports; {total_diag} records with sanitizer output; {total_fix} with fix data; all source-body byte checks passed')


if __name__ == '__main__':
    render()

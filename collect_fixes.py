"""Fetch PR and commit fix data for all issues listed in bugs.txt."""
import concurrent.futures
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / 'taxos' / 'micro_taxo' / 'sources'
FIXES = ROOT / 'taxos' / 'micro_taxo' / 'sources' / 'fixes'
NUMBERS = re.findall(r'/issues/(\d+)', (ROOT / 'taxos' / 'bugs.txt').read_text())

LINKED_PRS = re.compile(r'<!-- gh-linked-prs -->(.*?)<!-- /gh-linked-prs -->', re.S)
GH_PR_REF = re.compile(r'\bgh-(\d+)\b')
PR_URL = re.compile(r'https://github\.com/python/cpython/pull/(\d+)')
COMMIT_URL = re.compile(r'https://github\.com/python/cpython/commit/([0-9a-f]{7,40})')


def api(endpoint):
    for attempt in range(4):
        r = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout)
        time.sleep(2 ** attempt)
    raise RuntimeError(r.stderr.strip())


def api_paginated(endpoint):
    results = []
    page = 1
    while True:
        sep = '&' if '?' in endpoint else '?'
        batch = api(f'{endpoint}{sep}per_page=100&page={page}')
        results.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return results


def collect_pr(number):
    path = FIXES / f'pr_{number}.json'
    if path.exists():
        return number, 'cached'
    pr = api(f'repos/python/cpython/pulls/{number}')
    files = api_paginated(f'repos/python/cpython/pulls/{number}/files')
    review_comments = api_paginated(f'repos/python/cpython/pulls/{number}/comments')
    issue_comments = api_paginated(f'repos/python/cpython/issues/{number}/comments')
    data = {
        'pr': pr,
        'files': files,
        'review_comments': review_comments,
        'issue_comments': issue_comments,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return number, f'{len(files)} files, {len(review_comments)} review comments'


def collect_commit(sha):
    path = FIXES / f'commit_{sha}.json'
    if path.exists():
        return sha, 'cached'
    commit = api(f'repos/python/cpython/commits/{sha}')
    path.write_text(json.dumps(commit, ensure_ascii=False, indent=2) + '\n')
    return sha, f'{len(commit.get("files", []))} files'


def gather_refs():
    pr_numbers = set()
    commit_shas = set()
    for n in NUMBERS:
        src = SOURCES / f'gh_{n}.json'
        if not src.exists():
            continue
        d = json.loads(src.read_text())
        all_objects = [d['issue'], *d['comments']]
        issue_body = d['issue'].get('body') or ''
        m = LINKED_PRS.search(issue_body)
        if m:
            for p in GH_PR_REF.findall(m.group(1)):
                pr_numbers.add(p)
        for obj in all_objects:
            text = obj.get('body') or ''
            for p in PR_URL.findall(text):
                pr_numbers.add(p)
            for sha in COMMIT_URL.findall(text):
                commit_shas.add(sha)
    return sorted(pr_numbers, key=int), sorted(commit_shas)


if __name__ == '__main__':
    FIXES.mkdir(parents=True, exist_ok=True)
    prs, commits = gather_refs()
    print(f'Collecting {len(prs)} PRs and {len(commits)} standalone commits...')

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        pr_futures = {pool.submit(collect_pr, p): p for p in prs}
        for f in concurrent.futures.as_completed(pr_futures):
            try:
                print('PR', *f.result(), flush=True)
            except Exception as e:
                print('FAILED PR', pr_futures[f], str(e), flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        commit_futures = {pool.submit(collect_commit, sha): sha for sha in commits}
        for f in concurrent.futures.as_completed(commit_futures):
            try:
                print('COMMIT', *f.result(), flush=True)
            except Exception as e:
                print('FAILED COMMIT', commit_futures[f], str(e), flush=True)

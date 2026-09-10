"""Archive public issue bodies and every discussion page without normalizing text."""
import concurrent.futures
import datetime
import json
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / 'sources'


def api(endpoint):
    for attempt in range(4):
        result = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        time.sleep(2 ** attempt)
    raise RuntimeError(result.stderr)


def collect(number):
    path = SOURCES / f'gh_{number}.json'
    if path.exists():
        return number, 'cached'
    issue = api(f'repos/python/cpython/issues/{number}')
    comments = []
    if issue['comments']:
        page = 1
        while True:
            batch = api(f'repos/python/cpython/issues/{number}/comments?per_page=100&page={page}')
            comments.extend(batch)
            if len(batch) < 100:
                break
            page += 1
    data = {'retrieved_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'issue': issue, 'comments': comments}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return number, f'{len(comments)} comments'


if __name__ == '__main__':
    SOURCES.mkdir(parents=True, exist_ok=True)
    numbers = re.findall(r'/issues/(\d+)', (ROOT.parent / 'bugs.txt').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(collect, n): n for n in dict.fromkeys(numbers)}
        for future in concurrent.futures.as_completed(futures):
            try:
                print(*future.result(), flush=True)
            except Exception as exc:
                print('FAILED', futures[future], str(exc), flush=True)

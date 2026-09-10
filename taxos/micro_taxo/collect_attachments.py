"""Download text attachments linked in issue bodies and comments."""
import concurrent.futures
import hashlib
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
dest = root / 'sources' / 'attachments'
dest.mkdir(parents=True, exist_ok=True)

urls = {}
for p in (root / 'sources').glob('gh_*.json'):
    d = json.loads(p.read_text())
    for obj in [d['issue'], *d['comments']]:
        for url in re.findall(
            r'https://github\.com/(?:[^\s<>]+?/files/|user-attachments/files/)[^\s<>\)\]"`]+',
            obj.get('body') or ''
        ):
            url = url.rstrip(';,.:')
            if re.search(r'\.(txt|log|out|patch|py|c)$', url, re.I):
                urls.setdefault(url, []).append(obj['html_url'])


def get(item):
    url, refs = item
    name = hashlib.sha256(url.encode()).hexdigest()[:12] + '_' + url.rsplit('/', 1)[-1]
    path = dest / name
    r = subprocess.run(
        ['curl', '--fail', '--silent', '--show-error', '--location', '--max-time', '90',
         url, '--output', str(path)],
        capture_output=True, text=True
    )
    out = {'url': url, 'references': refs, 'path': name, 'success': r.returncode == 0}
    if r.returncode:
        out['error'] = r.stderr
    else:
        out['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(name, out['success'], flush=True)
    return out


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(get, urls.items()))
(dest / 'manifest.json').write_text(json.dumps(results, indent=2) + '\n')

import json
import os
from collections import defaultdict, Counter

cluster_counts = Counter()
cluster_issues = defaultdict(list)

os.chdir("taxos/workflow_signatures")

for f in os.listdir('.'):
    if f.startswith('gh_') and f.endswith('.json'):
        with open(f) as fp:
            d = json.load(fp)
        cid = d.get('cluster_id')
        issue = d.get('issue')
        if cid:
            cluster_counts[cid] += 1
            cluster_issues[cid].append(issue)

with open('clusters.json') as fp:
    clusters = json.load(fp)['clusters']

print(f'Total workflows: {len(cluster_counts)}')
print()
print(f'{"Rank":<5} {"Cluster":<18} {"Count":<7} Summary')
print('-' * 90)
for i, (cid, count) in enumerate(cluster_counts.most_common(20), 1):
    summary = clusters.get(cid, {}).get('summary', '(no summary)')
    print(f'{i:<5} {cid:<18} {count:<7} {summary[:60]}')

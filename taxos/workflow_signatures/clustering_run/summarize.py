"""Summarize the completed clustering run as ranked Pareto data and a report."""
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
state = json.loads((ROOT.parent / 'clusters.json').read_text())
if not state['review']['complete']:
    raise SystemExit('Review is incomplete; final Pareto output was not written.')
initial = json.loads((ROOT / 'initial_clusters.json').read_text())


def summarize(state):
    clusters = sorted(state['clusters'].items(), key=lambda item: (-len(item[1]['issues']), item[0]))
    total = sum(len(c['issues']) for _, c in clusters)
    cumulative = 0
    rows = []
    for rank, (key, cluster) in enumerate(clusters, 1):
        size = len(cluster['issues'])
        cumulative += size
        rows.append({'rank': rank, 'cluster_id': key, 'summary': cluster['summary'], 'size': size,
                     'issue_percent': round(100 * size / total, 4), 'cumulative_issues': cumulative,
                     'cumulative_percent': round(100 * cumulative / total, 4), 'issues': cluster['issues']})
    k80 = next(row['rank'] for row in rows if row['cumulative_issues'] >= .8 * total)
    k20 = math.ceil(.2 * len(rows))
    return {'issues': total, 'clusters': len(rows), 'singletons': sum(row['size'] == 1 for row in rows),
            'size_distribution': dict(sorted(Counter(row['size'] for row in rows).items())),
            'clusters_for_80_percent': k80, 'cluster_percent_for_80_percent': 100 * k80 / len(rows),
            'top_20_percent_cluster_count': k20, 'top_20_percent_issue_coverage': rows[k20 - 1]['cumulative_percent'],
            'ranked_clusters': rows}

before, after = summarize(initial), summarize(state)
assert before['issues'] == after['issues'] == len(state['review']['decisions'])
result = {'manual_revision': state.get('manual_revision'), 'initial': before, 'reviewed': after, 'review_actions': dict(Counter(e['action'] for e in state['review']['decisions']))}
(ROOT / 'pareto_data.json').write_text(json.dumps(result, indent=2) + '\n')
lines = ['# Workflow clustering Pareto analysis', '',
         f"{after['issues']} existing workflows; no signatures regenerated.", '',
         ('| Metric | CPU clustering | After manual revision |' if state.get('manual_revision') else '| Metric | CPU clustering | After Luna review |'), '|---|---:|---:|',
         f"| Clusters | {before['clusters']} | {after['clusters']} |",
         f"| Singletons | {before['singletons']} | {after['singletons']} |", '',
         f"The largest {after['clusters_for_80_percent']} clusters ({after['cluster_percent_for_80_percent']:.1f}% of clusters) cover at least 80% of workflows.",
         f"The largest {after['top_20_percent_cluster_count']} clusters (rounded up from 20%) cover {after['top_20_percent_issue_coverage']:.1f}% of workflows.", '',
         ('These frequencies reflect a manual constraint restoring the original top five exactly; they are not an unconstrained clustering result. No Pareto power-law fit is assumed.' if state.get('manual_revision') else 'These are empirical ranked frequencies; no Pareto power-law fit is assumed.'), '',
         '## Cluster-size frequency', '', '| Workflows per cluster | Number of clusters |', '|---:|---:|']
lines += [f'| {size} | {count} |' for size, count in after['size_distribution'].items()]
lines += ['', '## Ranked clusters', '', '| Rank | Cluster | Workflows | Cumulative workflows | Cumulative % |', '|---:|---|---:|---:|---:|']
lines += [f"| {r['rank']} | {r['cluster_id']} | {r['size']} | {r['cumulative_issues']} | {r['cumulative_percent']:.2f} |" for r in after['ranked_clusters']]
(ROOT / 'pareto_report.md').write_text('\n'.join(lines) + '\n')

print(json.dumps({k: v for k, v in after.items() if k != 'ranked_clusters'}, indent=2))
print('Review actions:', result['review_actions'])

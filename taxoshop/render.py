"""Render canonical artifacts, including exact sanitizer text, as Markdown."""
import re

from .artifacts import encode


def fence(text, language='text'):
    delimiter = '`' * max(3, max((len(m) for m in re.findall(r'`+', text)), default=0) + 1)
    return delimiter + language + '\n' + text + ('' if text.endswith('\n') else '\n') + delimiter + '\n'


def label(text):
    return str(text).replace('_', ' ').capitalize()


def render_value(value, level=3):
    if isinstance(value, dict):
        if {'statement', 'basis', 'id'} <= value.keys():
            return f"**{value['id']} ({value['basis']})**: {value['statement']}\n\nEvidence: {', '.join(value['evidence_refs']) or 'none'}. {value['rationale']}\n"
        if {'text', 'basis', 'micro_claim_refs'} <= value.keys():
            refs = ', '.join(f"{r['defect_id']}@{r['report_version']}:{r['claim_id']}" for r in value['micro_claim_refs'])
            return f"{value['text']}\n\nBasis: {value['basis']}; {refs or 'proposed guidance'}. {value['rationale']}\n"
        return '\n'.join('#' * min(level, 6) + ' ' + label(k) + '\n\n' + render_value(v, level + 1) for k, v in value.items())
    if isinstance(value, list):
        return '\n\n'.join(render_value(v, level) for v in value) if value else 'None recorded.\n'
    return ('Unknown' if value is None else str(value)) + '\n'


def micro_markdown(report):
    parts = [f"# Bug analysis: {report['defect_id']}\n", '## Sources\n', '\n'.join(report['issue_urls'])]
    for key in ['context', 'preconditions', 'causal_trace', 'violated_invariant', 'root_cause', 'existing_protections', 'consequence', 'fix', 'reproduction', 'mechanism_signature', 'quality', 'relationships']:
        parts.extend(['\n## ' + label(key) + '\n', render_value(report[key])])
    logs = report['sanitizer_output']
    parts.extend(['\n## Full sanitizer output\n', f"Status: **{logs['status']}**. {logs['rationale']}\n"])
    for output in logs['outputs']:
        parts.extend([f"\n### {output['id']} — {output['sanitizer']}\n",
                      f"Origin: {output['origin']}; completeness: {output['completeness']}; evidence: {', '.join(output['evidence_refs'])}.\n\nSHA-256: `{output['raw_output_sha256']}`\n",
                      fence(output['raw_output'])])
    parts.extend(['\n## Evidence inventory\n', fence(encode(report['evidence']), 'json'), '\n## Run provenance\n', fence(encode(report['provenance']), 'json')])
    return '\n'.join(parts)


def catalog_markdown(catalog):
    parts = [f"# Pattern catalog: {catalog['catalog_id']}\n", f"Method: {catalog['method']}\n"]
    for pattern in catalog['patterns']:
        parts.extend([f"\n## {pattern['pattern_id']}: {pattern['name']}\n", render_value(pattern)])
        memberships = [m for m in catalog['memberships'] if m['pattern_id'] == pattern['pattern_id']]
        parts.extend(['\n### Membership decisions\n', render_value(memberships)])
    parts.extend(['\n## Unassigned defects\n', render_value(catalog['unassigned_defects'])])
    return '\n'.join(parts)


def agent_guide(catalog):
    parts = ['# Bug-search guide\n', 'These patterns guide investigation. Proposed tests are unexecuted; each candidate finding still needs validation.\n']
    if not any(p['status'] != 'retired' for p in catalog['patterns']):
        parts.append('No supported patterns were synthesized from these inputs.\n')
    for pattern in catalog['patterns']:
        if pattern['status'] == 'retired':
            continue
        support = [m['defect_id'] for m in catalog['memberships'] if m['pattern_id'] == pattern['pattern_id'] and m['decision'] == 'accepted']
        parts.extend([f"\n## {pattern['name']} ({pattern['pattern_id']}, {pattern['status']})\n", f"Supporting canonical defects: {', '.join(support) or 'none'}\n"])
        for key in ['mechanism', 'membership_conditions', 'exclusion_conditions', 'boundaries', 'search_guide', 'repair_principle', 'limitations']:
            parts.extend(['\n### ' + label(key) + '\n', render_value(pattern[key], 4)])
    if catalog['unassigned_defects']:
        parts.extend(['\n## Unassigned defects\n', render_value(catalog['unassigned_defects'])])
    return '\n'.join(parts)

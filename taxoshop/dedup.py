"""Diagnostic similarity candidates, never automatic canonical defect merges."""
import re
from collections import defaultdict

from .artifacts import digest


def normalized_trace(text):
    lines = []
    for line in text.splitlines():
        if re.search(r'^\s*#\d+\s|SUMMARY:|ERROR:.*Sanitizer|runtime error:', line):
            line = re.sub(r'==\d+==', '==PID==', line)
            line = re.sub(r'0x[0-9a-fA-F]+', '<address>', line)
            lines.append(line.strip())
    return '\n'.join(lines)


def candidates(reports):
    exact, normalized = defaultdict(set), defaultdict(set)
    incomplete = []
    for report in reports:
        section = report['sanitizer_output']
        if section['status'] in ('partial', 'unavailable'):
            incomplete.append(report['defect_id'])
        for output in section['outputs']:
            exact[output['raw_output_sha256']].add(report['defect_id'])
            trace = normalized_trace(output['raw_output'])
            if trace:
                normalized[digest(trace)].add(report['defect_id'])
    return {'schema_version': '0.1.0', 'normalization': 'sanitizer-stack-v1',
            'interpretation': 'Candidate duplicate groups only. Confirm against full diagnostics and causal evidence; this command never merges defects.',
            'incomplete_sanitizer_evidence': incomplete,
            'exact_output_matches': [sorted(group) for group in exact.values() if len(group) > 1],
            'normalized_trace_matches': [sorted(group) for group in normalized.values() if len(group) > 1]}

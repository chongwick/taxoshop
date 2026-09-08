"""Structural validation plus evidence, membership, and artifact integrity checks."""
from __future__ import annotations

from copy import deepcopy
import re

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from .artifacts import ROOT, digest, inside, read_json

SCHEMAS = {p.name: read_json(p) for p in (ROOT / 'schemas').glob('*.json')}
BASE = 'https://taxoshop.local/schemas/'
REGISTRY = Registry().with_resources((BASE + name, Resource.from_contents(value)) for name, value in SCHEMAS.items())


def schema(name):
    return deepcopy(SCHEMAS[name + '.schema.json'])


def validate_schema(data, name):
    spec = schema(name)
    spec['$id'] = BASE + name + '.schema.json'
    validator = Draft202012Validator(spec, registry=REGISTRY, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda e: str(list(e.path)))
    if errors:
        raise ValueError('\n'.join(f'{"/".join(map(str, e.path))}: {e.message}' for e in errors[:20]))


def expanded_schema(spec):
    if isinstance(spec, list):
        return [expanded_schema(v) for v in spec]
    if not isinstance(spec, dict):
        return spec
    if '$ref' in spec:
        file, pointer = spec['$ref'].split('#', 1)
        target = SCHEMAS[file]
        for segment in pointer.lstrip('/').split('/'):
            target = target[segment]
        return expanded_schema(target)
    return {k: expanded_schema(v) for k, v in spec.items()}


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def unique(items, key, label):
    result = {}
    for item in items:
        if item[key] in result:
            raise ValueError(f'Duplicate {label}: {item[key]}')
        result[item[key]] = item
    return result


def claims(report):
    return unique([n for n in walk(report) if {'id', 'statement', 'basis'} <= n.keys()], 'id', 'claim ID')


def validate_micro(report, root=None):
    validate_schema(report, 'micro-report')
    evidence = unique(report['evidence'], 'id', 'evidence ID')
    for item in evidence.values():
        if item['kind'] in ('source', 'patch', 'test') and not re.fullmatch(r'[0-9a-fA-F]{40}', item['revision'] or ''):
            raise ValueError('Source, patch, and test evidence must identify a full commit SHA')
    claims(report)
    for node in walk(report):
        for identifier in node.get('evidence_refs', []):
            if identifier not in evidence:
                raise ValueError(f'Unknown evidence reference: {identifier}')
    if [s['step'] for s in report['causal_trace']] != list(range(1, len(report['causal_trace']) + 1)):
        raise ValueError('Causal trace steps must be consecutive and ordered')
    if report['fix']['status'] == 'identified':
        refs = report['fix']['behavioral_change']['evidence_refs']
        if not any(evidence[r]['kind'] == 'patch' for r in refs):
            raise ValueError('Identified fix must cite patch evidence')
    reproduction = report['reproduction']
    if reproduction['status'] in ('reproduced', 'not_reproduced'):
        if not any(evidence[r]['kind'] == 'execution_log' for r in reproduction['evidence_refs']):
            raise ValueError('Execution status requires an execution log')
    outputs = report['sanitizer_output']['outputs']
    unique(outputs, 'id', 'sanitizer output ID')
    texts = {}
    if root is not None:
        for item in evidence.values():
            path = inside(root, item['artifact_path'])
            raw = path.read_bytes()
            if digest(raw) != item['sha256']:
                raise ValueError(f'Evidence hash mismatch: {item["id"]}')
            texts[item['id']] = raw.decode('utf-8', errors='replace')
        if reproduction['input_artifact'] is not None:
            if not inside(root, reproduction['input_artifact']).is_file():
                raise ValueError('Missing reproduction input artifact')
    for output in outputs:
        if digest(output['raw_output']) != output['raw_output_sha256']:
            raise ValueError('Sanitizer output hash mismatch')
        if texts and not any(output['raw_output'] in texts[r] for r in output['evidence_refs']):
            raise ValueError('Sanitizer output is not verbatim source evidence')
    if report['quality']['synthesis_eligibility'] == 'eligible':
        if report['quality']['defect_status'] != 'confirmed':
            raise ValueError('Only confirmed defects are eligible for accepted pattern support')
        essentials = [report['root_cause'], report['violated_invariant'], *report['preconditions'], *[s['event'] for s in report['causal_trace']]]
        if any(c['basis'] == 'unknown' for c in essentials):
            raise ValueError('Eligible report has unknown necessary causal claims')
    return report


def validate_catalog(catalog, reports, root=None):
    validate_schema(catalog, 'pattern-catalog')
    report_map = unique(reports, 'defect_id', 'defect ID')
    inputs = unique(catalog['input_reports'], 'defect_id', 'catalog input')
    if set(inputs) != set(report_map):
        raise ValueError('Catalog input reports differ from supplied reports')
    if set(catalog['configuration']['input_order']) != set(inputs):
        raise ValueError('Input order must be a permutation of input defect IDs')
    for identifier, item in inputs.items():
        if item['report_version'] != report_map[identifier]['report_version']:
            raise ValueError('Input report version mismatch')
        if root is not None and digest(inside(root, item['artifact_path']).read_bytes()) != item['sha256']:
            raise ValueError('Input report hash mismatch')
    pattern_map = unique(catalog['patterns'], 'pattern_id', 'pattern ID')
    claim_maps = {key: claims(report) for key, report in report_map.items()}

    def check_refs(refs, defect=None, known=False):
        for ref in refs:
            identifier = ref['defect_id']
            if identifier not in report_map or ref['report_version'] != report_map[identifier]['report_version']:
                raise ValueError('Unknown report or report version in micro claim reference')
            claim = claim_maps[identifier].get(ref['claim_id'])
            if claim is None or (defect is not None and identifier != defect):
                raise ValueError('Unknown or wrong-member micro claim reference')
            if known and claim['basis'] == 'unknown':
                raise ValueError('Unknown micro claim cannot support acceptance')

    for node in walk(catalog):
        if 'micro_claim_refs' in node:
            check_refs(node['micro_claim_refs'], known=node.get('basis') == 'corpus_supported')
    accepted = {key: set() for key in pattern_map}
    seen = set()
    for membership in catalog['memberships']:
        defect, pid = membership['defect_id'], membership['pattern_id']
        if (defect, pid) in seen:
            raise ValueError('Duplicate membership pair')
        seen.add((defect, pid))
        if defect not in report_map or pid not in pattern_map:
            raise ValueError('Membership refers to unknown defect or pattern')
        if membership['report_version'] != report_map[defect]['report_version']:
            raise ValueError('Membership version mismatch')
        pattern = pattern_map[pid]
        necessary = unique(pattern['membership_conditions'], 'id', 'condition ID')
        exclusions = unique(pattern['exclusion_conditions'], 'id', 'exclusion ID')
        if set(necessary) & set(exclusions):
            raise ValueError('Condition and exclusion IDs overlap')
        checks = unique(membership['condition_checks'], 'condition_id', 'condition check')
        if set(checks) != set(necessary) | set(exclusions):
            raise ValueError('Membership must evaluate every condition and exclusion exactly once')
        roles = unique(pattern['roles'], 'id', 'role ID')
        bindings = unique(membership['role_bindings'], 'role_id', 'role binding')
        if not set(bindings) <= set(roles):
            raise ValueError('Unknown role binding')
        for check in checks.values():
            check_refs(check['micro_claim_refs'], defect, known=membership['decision'] == 'accepted')
        for binding in bindings.values():
            check_refs(binding['micro_claim_refs'], defect, known=membership['decision'] == 'accepted')
        if membership['decision'] == 'accepted':
            if pattern['status'] == 'retired' or report_map[defect]['quality']['synthesis_eligibility'] != 'eligible':
                raise ValueError('Cannot accept retired patterns or ineligible reports')
            if set(bindings) != set(roles):
                raise ValueError('Accepted member must bind every role')
            for cid, check in checks.items():
                expected = 'satisfied' if cid in necessary else 'not_satisfied'
                if check['outcome'] != expected or not check['micro_claim_refs']:
                    raise ValueError('Acceptance requires evidence for every necessary and exclusion predicate')
            accepted[pid].add(defect)
        elif membership['decision'] == 'rejected':
            failures = [c for cid, c in checks.items() if c['outcome'] == ('not_satisfied' if cid in necessary else 'satisfied') and c['micro_claim_refs']]
            if not failures:
                raise ValueError('Rejection requires an evidenced failed predicate')
            for check in failures:
                check_refs(check['micro_claim_refs'], defect, known=True)
    # Canonical defect IDs are supplied by the corpus manifest. Resolve alias chains,
    # including two inputs that both refer to an external canonical ID.
    parents = {}
    def representative(identifier):
        parents.setdefault(identifier, identifier)
        while parents[identifier] != identifier:
            identifier = parents[identifier]
        return identifier
    for defect, report in report_map.items():
        for relation in report['relationships']:
            if relation['kind'] in ('duplicate', 'backport'):
                parents[representative(defect)] = representative(relation['target'])
    for pid, pattern in pattern_map.items():
        members = accepted[pid]
        independent = {representative(d) for d in members}
        if pattern['status'] == 'recurrent' and len(independent) < 2:
            raise ValueError('Recurrent patterns require two independent canonical defects')
        unique(pattern['roles'], 'id', 'role ID')
        unique(pattern['membership_conditions'] + pattern['exclusion_conditions'], 'id', 'condition ID')
    graph = {pid: [] for pid in pattern_map}
    for pid, pattern in pattern_map.items():
        for relation in pattern['relations']:
            parent = relation['target_pattern_id']
            if parent not in graph or parent == pid:
                raise ValueError('Invalid pattern relation')
            if relation['kind'] == 'specializes':
                graph[pid].append(parent)
                # This release requires explicit inherited predicate text.
                child = {c['description']['text'] for c in pattern['membership_conditions']}
                required = {c['description']['text'] for c in pattern_map[parent]['membership_conditions']}
                if not required <= child:
                    raise ValueError('Specialization must explicitly retain parent conditions')
    def visit(pid, path):
        if pid in path:
            raise ValueError('Specialization cycle')
        for parent in graph[pid]:
            visit(parent, path | {pid})
    for pid in graph:
        visit(pid, set())
    assigned = set().union(*accepted.values()) if accepted else set()
    unassigned = unique(catalog['unassigned_defects'], 'defect_id', 'unassigned defect')
    if set(unassigned) != set(report_map) - assigned:
        raise ValueError('Unassigned list must cover exactly defects without accepted memberships')
    return catalog

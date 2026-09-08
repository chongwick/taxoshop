"""Canonical splits, explicit external review, and descriptive search outcomes."""
from __future__ import annotations

import math
import random
from pathlib import Path

from .artifacts import content_hash, digest, inside, now, read_json, write, write_json
from .contracts import unique, validate_schema
from .macro import load_reports


def identity_keys(report):
    keys = {'defect:' + report['defect_id']}
    keys.update('issue:' + url for url in report['issue_urls'])
    for relation in report['relationships']:
        if relation['kind'] in ('duplicate', 'backport'):
            target = relation['target']
            keys.add(('issue:' if target.startswith('https://') else 'defect:') + target)
    return sorted(keys)


def validate_split(split):
    validate_schema(split, 'split')
    unique(split['reports'], 'defect_id', 'split defect ID')
    if sum(split['fractions'].values()) >= 1:
        raise ValueError('Split fractions must leave a discovery partition')
    assignments = {}
    groups = {}
    for item in split['reports']:
        for key in item['identity_keys']:
            value = (item['partition'], item['canonical_group'])
            if key in assignments and assignments[key] != value:
                raise ValueError('Canonical identity crosses split partitions or groups')
            assignments[key] = value
        group = item['canonical_group']
        if group in groups and groups[group] != item['partition']:
            raise ValueError('Canonical group crosses split partitions')
        groups[group] = item['partition']
        if 'defect:' + item['defect_id'] not in item['identity_keys']:
            raise ValueError('Split identity keys omit the defect ID')
    return split


def create_split(input_dir, output, *, seed=0, development=0.2, evaluation=0.2):
    if not all(math.isfinite(v) and 0 <= v < 1 for v in (development, evaluation)) or development + evaluation >= 1:
        raise ValueError('Fractions must be nonnegative and sum to less than one')
    if Path(output).exists():
        raise ValueError('Split output already exists; choose a new file to preserve the frozen split')
    loaded = load_reports(input_dir)
    parents = {}
    def find(key):
        parents.setdefault(key, key)
        if parents[key] != key:
            parents[key] = find(parents[key])
        return parents[key]
    identities = {}
    for report, _ in loaded:
        keys = identity_keys(report)
        identities[report['defect_id']] = keys
        for key in keys[1:]:
            parents[find(key)] = find(keys[0])
    groups = {}
    for identifier, keys in identities.items():
        groups.setdefault(find(keys[0]), []).append(identifier)
    units = sorted(sorted(ids) for ids in groups.values())
    random.Random(seed).shuffle(units)
    n_dev, n_eval = int(len(units) * development), int(len(units) * evaluation)
    partitions = {}
    canonical = {}
    for index, unit in enumerate(units):
        part = 'evaluation' if index < n_eval else 'development' if index < n_eval + n_dev else 'discovery'
        for identifier in unit:
            partitions[identifier] = part
            canonical[identifier] = min(unit)
    split = {'schema_version': '0.1.0', 'seed': seed, 'input_run_sha256': digest((Path(input_dir) / 'run.json').read_bytes()),
             'fractions': {'development': development, 'evaluation': evaluation},
             'reports': [{'defect_id': r['defect_id'], 'sha256': digest(p.read_bytes()), 'partition': partitions[r['defect_id']],
                          'canonical_group': canonical[r['defect_id']], 'identity_keys': identities[r['defect_id']]} for r, p in sorted(loaded, key=lambda pair: pair[0]['defect_id'])]}
    validate_split(split)
    write_json(output, split)
    return split


def review_template(input_dir, output):
    from .hunt import load_hunt
    _, report = load_hunt(input_dir)
    if Path(output).exists():
        raise ValueError('Review output already exists; refusing to overwrite decisions')
    template = {'schema_version': '0.1.0', 'hunt_report_sha256': digest((Path(input_dir) / 'findings.json').read_bytes()),
                'reviewer': '', 'reviewed_at': now(), 'decisions': [
                    {'finding_id': f['finding_id'], 'decision': 'uncertain', 'canonical_defect_id': None,
                     'discovery_kind': 'unknown', 'rationale': 'Not yet reviewed.', 'execution': None, 'upstream_url': None}
                    for f in report['findings']]}
    write_json(output, template)
    return template


def validate_review(review, report, root, report_sha256):
    validate_schema(review, 'hunt-review')
    if not review['reviewer'].strip():
        raise ValueError('Review must identify the reviewer')
    if review['hunt_report_sha256'] != report_sha256:
        raise ValueError('Review does not match the frozen hunt report')
    decisions = unique(review['decisions'], 'finding_id', 'review decision')
    if set(decisions) != {f['finding_id'] for f in report['findings']}:
        raise ValueError('Review must decide every candidate exactly once')
    for decision in decisions.values():
        execution = decision['execution']
        if decision['decision'] == 'validated':
            if execution is None or not decision['canonical_defect_id']:
                raise ValueError('Validated findings require a canonical defect ID and execution evidence')
        elif decision['canonical_defect_id'] is not None or decision['discovery_kind'] != 'unknown':
            raise ValueError('Unvalidated candidates cannot claim canonical identity or novelty')
        if execution is not None:
            if execution['revision'] != report['target_revision']:
                raise ValueError('Execution must use the pinned hunt target revision')
            for prefix in ('log', 'reproducer'):
                raw = inside(root, execution[prefix + '_path']).read_bytes()
                if not raw or digest(raw) != execution[prefix + '_sha256']:
                    raise ValueError(f'Review {prefix} evidence is empty or has a hash mismatch')
    return review


def evaluate(run_dirs, output, *, review_paths=()):
    """No proposed command is executed. Validated means reviewer-attested evidence."""
    from .hunt import load_hunt
    if not run_dirs:
        raise ValueError('At least one hunt run is required')
    root = Path(output)
    if root.exists() and any(root.iterdir()):
        raise ValueError('Evaluation output must be empty')
    reviews = {}
    for path in review_paths:
        review = read_json(path)
        validate_schema(review, 'hunt-review')
        sha = review['hunt_report_sha256']
        if sha in reviews:
            raise ValueError('More than one review supplied for the same hunt')
        reviews[sha] = (review, Path(path))
    rows, archive, used, run_ids, canonical_kinds = [], {}, set(), set(), {}
    for index, directory in enumerate(run_dirs, 1):
        directory = Path(directory)
        manifest, report = load_hunt(directory, allow_failed=True)
        if manifest['status'] == 'running':
            raise ValueError('Cannot evaluate a running or interrupted hunt; resume it first')
        if manifest['run_id'] in run_ids:
            raise ValueError('Duplicate hunt run; use distinct seed labels for repetitions')
        run_ids.add(manifest['run_id'])
        prefix = f'inputs/run-{index:04d}/'
        paths = set(manifest['artifacts']) | {'run.json'}
        paths.update(str(p.relative_to(directory)) for p in (directory / 'calls').glob('*') if p.is_file())
        review = None
        if report is not None:
            paths.add('findings.json')
            sha = manifest['report_sha256']
            if sha in reviews:
                review, review_path = reviews[sha]
                validate_review(review, report, review_path.parent, sha)
                used.add(sha)
                archive[prefix + 'review/' + review_path.name] = review_path.read_bytes()
                # Keep the original filename and relative evidence paths together
                # so the exported review remains independently validatable.
                for decision in review['decisions']:
                    if decision['execution']:
                        for kind in ('log', 'reproducer'):
                            relative = decision['execution'][kind + '_path']
                            path = inside(review_path.parent, relative)
                            # Canonical relative names keep the exported review resolvable.
                            if Path(relative).is_absolute() or '..' in Path(relative).parts:
                                raise ValueError('Review evidence paths must be relative without parent traversal')
                            archive[prefix + 'review/' + relative] = path.read_bytes()
        for path in paths:
            archive[prefix + path] = inside(directory, path).read_bytes()
        decisions = review['decisions'] if review else []
        validated = [d for d in decisions if d['decision'] == 'validated']
        for decision in validated:
            cid, kind = decision['canonical_defect_id'], decision['discovery_kind']
            if cid in canonical_kinds and canonical_kinds[cid] != kind:
                raise ValueError('Conflicting discovery classifications for a canonical defect')
            canonical_kinds[cid] = kind
        count = len(report['findings']) if report is not None else None
        usages = [read_json(p) for p in sorted((directory / 'calls').glob('*.usage.json'))]
        def tokens(field):
            values = [u.get(field) for u in usages]
            # A failed model invocation has no usage record; unknown stays unknown.
            if list((directory / 'calls').glob('*.error.json')):
                return None
            return sum(values) if values and all(isinstance(v, int) and not isinstance(v, bool) for v in values) else None
        config = manifest['config']
        comparison = {key: config[key] for key in ('target_revision', 'sources', 'model', 'model_settings', 'attempts',
                      'max_prompt_chars', 'max_source_bytes', 'max_documentation_chars', 'max_findings', 'search_policy', 'implementation_sha256', 'packages')}
        # Replay content differs between conditions, so replay is deliberately
        # never treated as a real controlled comparison.
        rows.append({'hunt_id': manifest['run_id'], 'condition': config['condition'], 'seed': config['seed'],
                     'status': manifest['status'], 'error': manifest.get('error'), 'artifact_directory': prefix.rstrip('/'),
                     'comparison_key': content_hash(comparison), 'split_sha256': config['split_sha256'],
                     'review_evidence_root': prefix + 'review' if review else None,
                     'review_path': prefix + 'review/' + review_path.name if review else None,
                     'reviewed': review is not None, 'candidates': count, 'validated_candidates': len(validated) if review else None,
                     'rejected_candidates': sum(d['decision'] == 'rejected' for d in decisions) if review else None,
                     'uncertain_candidates': sum(d['decision'] == 'uncertain' for d in decisions) if review else None,
                     'distinct_validated_defects': sorted({d['canonical_defect_id'] for d in validated}) if review else None,
                     'validation_rate': len(validated) / count if review and count else None,
                     'input_tokens': tokens('input_tokens'), 'output_tokens': tokens('output_tokens'),
                     'elapsed_seconds': manifest['elapsed_seconds'],
                     'seconds_per_distinct_validated_defect': manifest['elapsed_seconds'] / len({d['canonical_defect_id'] for d in validated}) if validated else None,
                     'tokens_per_distinct_validated_defect': (tokens('input_tokens') + tokens('output_tokens')) / len({d['canonical_defect_id'] for d in validated}) if validated and tokens('input_tokens') is not None and tokens('output_tokens') is not None else None,
                     'documentation_characters': report['documentation_characters'] if report else None,
                     'response_replay': config['model'] == 'offline-response-replay'})
    if set(reviews) != used:
        raise ValueError('A supplied review has no matching completed hunt run')
    conditions = {}
    for condition in sorted({r['condition'] for r in rows}):
        selected = [r for r in rows if r['condition'] == condition]
        reviewed = [r for r in selected if r['reviewed']]
        distinct = sorted({cid for r in reviewed for cid in r['distinct_validated_defects']})
        candidate_count = sum(r['candidates'] for r in reviewed)
        validated_count = sum(r['validated_candidates'] for r in reviewed)
        conditions[condition] = {'runs': len(selected), 'failed_runs': sum(r['status'] == 'failed' for r in selected),
                                 'reviewed_runs': len(reviewed), 'unreviewed_completed_runs': sum(r['status'] == 'complete' and not r['reviewed'] for r in selected),
                                 'reviewed_candidates': candidate_count, 'validated_candidates': validated_count,
                                 'pooled_validation_rate': validated_count / candidate_count if candidate_count else None,
                                 'distinct_validated_defects': distinct if reviewed else None,
                                 'mean_distinct_validated_per_reviewed_run': sum(len(r['distinct_validated_defects']) for r in reviewed) / len(reviewed) if reviewed else None,
                                 'reviewer_classified_new': [cid for cid in distinct if canonical_kinds[cid] == 'new'],
                                 'historical_rediscoveries': [cid for cid in distinct if canonical_kinds[cid] == 'historical']}
    config_match = len({r['comparison_key'] for r in rows}) == 1
    split_match = len({r['split_sha256'] for r in rows if r['condition'] != 'none'}) <= 1
    summary = {'schema_version': '0.1.0', 'created_at': now(), 'runs': rows, 'conditions': conditions,
               'recorded_search_configurations_match': config_match, 'documentation_splits_match': split_match,
               'interpretation': 'Descriptive outcomes only. Validated defects are externally reviewer-attested, not automatically reproduced by Taxoshop. No causal treatment effect, upstream confirmation, or novelty is inferred. Failed and unreviewed runs are not zero-defect observations. Character ceilings are not token/spending budgets. Replay runs test mechanics only.',
               'artifact_sha256s': {p: digest(raw) for p, raw in sorted(archive.items())}}
    for path, raw in archive.items():
        write(inside(root, path), raw)
    write_json(root / 'summary.json', summary)
    lines = ['# Downstream search evaluation', '', summary['interpretation'], '',
             '| Condition | Runs | Failed | Reviewed | Reviewed candidates | Distinct validated |',
             '| --- | ---: | ---: | ---: | ---: | ---: |']
    for condition, result in conditions.items():
        distinct = result['distinct_validated_defects']
        lines.append(f'| {condition} | {result["runs"]} | {result["failed_runs"]} | {result["reviewed_runs"]} | {result["reviewed_candidates"]} | {len(distinct) if distinct is not None else "unknown"} |')
    lines += ['', f'Recorded search configurations match: {config_match}. Documentation splits match: {split_match}.',
              'Inspect per-run data, repeated seed labels, actual usage, missing reviews, and unequal documentation sizes before comparison.', '']
    write(root / 'summary.md', '\n'.join(lines))
    return summary

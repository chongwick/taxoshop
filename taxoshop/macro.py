"""Incremental induction and embedding proposals with shared reconciliation."""
from __future__ import annotations

import random
import time
from pathlib import Path

from .artifacts import ROOT, content_hash, digest, encode, environment, inside, now, provenance, read_json, write, write_json
from .clustering import SIGNATURE_VERSION, embedding_groups
from .contracts import expanded_schema, schema, validate_catalog, validate_micro
from .models import request
from .render import agent_guide, catalog_markdown

PROMPT = (ROOT / 'prompts/macro.md').read_text()
FIELDS = ['patterns', 'memberships', 'unassigned_defects', 'revision_log']


def load_reports(directory, allow_partial=False):
    directory = Path(directory)
    manifest = read_json(directory / 'run.json')
    if manifest['status'] != 'complete' and not allow_partial:
        raise ValueError('Micro run is incomplete; pass --allow-partial to explicitly use only completed reports')
    reports = []
    for identifier, item in manifest['items'].items():
        if item['status'] != 'complete':
            continue
        path = inside(directory, item['report_path'])
        if digest(path.read_bytes()) != item['report_sha256']:
            raise ValueError(f'Micro report hash mismatch: {identifier}')
        report = read_json(path)
        validate_micro(report, directory)
        if report['defect_id'] != identifier:
            raise ValueError('Report identity differs from micro manifest')
        reports.append((report, path))
    if not reports:
        raise ValueError('No completed micro reports')
    return reports


def analysis_view(report):
    """Full causal analysis; raw diagnostics stay in the copied canonical report."""
    return {key: value for key, value in report.items() if key not in ('sanitizer_output', 'provenance')}


def run_macro(input_dir, output, model, *, method='incremental', resume=False, allow_partial=False, seed=0,
              embedding_model='sentence-transformers/all-mpnet-base-v2', embedding_revision=None,
              threshold=0.3, attempts=2, max_prompt_chars=750_000, grouper=None, split_path=None, partition='discovery'):
    if method not in ('incremental', 'embedding'):
        raise ValueError('Unknown macro method')
    loaded = load_reports(input_dir, allow_partial)
    split = None
    if split_path is not None:
        from .evaluation import validate_split
        split = validate_split(read_json(split_path))
        if partition not in ('discovery', 'development'):
            raise ValueError('Catalog construction requires discovery or development inputs')
        allowed = {r['defect_id']: r for r in split['reports'] if r['partition'] == partition}
        loaded = [(r, p) for r, p in loaded if r['defect_id'] in allowed]
        if not loaded or any(digest(p.read_bytes()) != allowed[r['defect_id']]['sha256'] for r, p in loaded):
            raise ValueError('No matching frozen reports for selected split partition')
    loaded.sort(key=lambda pair: pair[0]['defect_id'])
    random.Random(seed).shuffle(loaded)
    reports = [r for r, _ in loaded]
    root = Path(output)
    inputs = [{'defect_id': r['defect_id'], 'report_version': r['report_version'], 'artifact_path': f'inputs/reports/{r["defect_id"]}.json', 'sha256': digest(p.read_bytes())} for r, p in loaded]
    env = environment()
    parameters = {'reconciliation': 'full-catalog', 'signature_serialization': SIGNATURE_VERSION, 'max_prompt_chars': max_prompt_chars,
                  'embedding_model': embedding_model if method == 'embedding' else None, 'embedding_revision': embedding_revision if method == 'embedding' else None,
                  'distance_metric': 'cosine' if method == 'embedding' else None, 'linkage': 'average' if method == 'embedding' else None,
                  'embedding_device': 'cpu' if method == 'embedding' else None,
                  'threshold': threshold if method == 'embedding' else None}
    config = {'input_reports': inputs, 'input_run_sha256': digest((Path(input_dir) / 'run.json').read_bytes()), 'method': method, 'seed': seed, 'parameters': parameters,
              'model': model.name, 'model_settings': model.settings, 'implementation_sha256': env['implementation_sha256'], 'packages': env['packages'], 'attempts': attempts, 'allow_partial': allow_partial,
              'split_sha256': content_hash(split) if split else None, 'partition': partition if split else None}
    manifest_path = root / 'run.json'
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        if not resume or manifest['config_sha256'] != content_hash(config):
            raise ValueError('Existing run requires --resume with unchanged configuration/inputs')
        if manifest['status'] == 'complete':
            catalog = read_json(root / 'catalog.json')
            if digest((root / 'catalog.json').read_bytes()) != manifest['catalog_sha256']:
                raise ValueError('Completed catalog was modified')
            validate_catalog(catalog, reports, root)
            for item in inputs:
                validate_micro(read_json(inside(root, item['artifact_path'])), root / 'inputs')
            return manifest
    else:
        if root.exists() and any(root.iterdir()):
            raise ValueError('New output directory must be empty')
        manifest = {'run_id': 'macro-' + content_hash(config)[:16], 'config_sha256': content_hash(config), 'config': config,
                    'environment': env, 'started_at': now(), 'status': 'running', 'steps': {}}
        for report, source in loaded:
            write(root / f'inputs/reports/{report["defect_id"]}.json', source.read_bytes())
            for evidence in report['evidence']:
                write(inside(root / 'inputs', evidence['artifact_path']), inside(input_dir, evidence['artifact_path']).read_bytes())
        write_json(root / 'input-run.json', read_json(Path(input_dir) / 'run.json'))
        if split:
            write_json(root / 'split.json', split)
    manifest['status'] = 'running'
    manifest.pop('error', None)
    write_json(manifest_path, manifest)
    started = time.monotonic()
    earlier_elapsed = manifest.get('elapsed_seconds', 0)
    catalog_schema = schema('pattern-catalog')
    response_schema = expanded_schema({'type': 'object', 'properties': {k: catalog_schema['properties'][k] for k in FIELDS}, 'required': FIELDS, 'additionalProperties': False})
    corpus_hash = content_hash(inputs)

    def step(key, subset, previous, instruction):
        ids = {r['defect_id'] for r in subset}
        step_inputs = [i for i in inputs if i['defect_id'] in ids]
        checkpoint = root / 'steps' / f'{key}.json'
        step_hash = content_hash({'reports': step_inputs, 'previous': previous, 'instruction': instruction})
        existing = manifest['steps'].get(key)
        if resume and existing:
            if existing['input_sha256'] != step_hash or digest(checkpoint.read_bytes()) != existing['output_sha256']:
                raise ValueError('Macro checkpoint changed')
            return validate_catalog(read_json(checkpoint), subset, root)
        def finalize(data):
            if set(data) != set(FIELDS):
                raise ValueError('Return exactly patterns, memberships, unassigned_defects, revision_log')
            catalog = {'schema_version': '0.1.0', 'catalog_id': manifest['run_id'], 'method': method, 'input_reports': step_inputs,
                       'configuration': {'input_order': [r['defect_id'] for r in subset], 'random_seed': seed, 'parameters': parameters},
                       **data, 'provenance': provenance(manifest['run_id'], corpus_hash, [i['sha256'] for i in step_inputs], model, PROMPT, time.monotonic() - started, [])}
            return validate_catalog(catalog, subset, root)
        prompt = PROMPT + '\nTask:\n' + instruction + '\nResponse schema:\n' + encode(response_schema) + '\nInput reports:\n' + encode([analysis_view(r) for r in subset]) + '\nPrevious catalog/proposals:\n' + encode(previous)
        if len(prompt) > max_prompt_chars:
            raise ValueError(f'Macro prompt exceeds {max_prompt_chars} characters ({len(prompt)}); no reports silently omitted. Use a smaller pilot or a larger explicit context budget.')
        print(f'Macro: {key} ({len(subset)} reports)', flush=True)
        result = request(model, key, prompt, root / 'calls', finalize, attempts, max_prompt_chars=max_prompt_chars)
        write_json(checkpoint, result)
        manifest['steps'][key] = {'input_sha256': step_hash, 'output_sha256': digest(checkpoint.read_bytes())}
        write_json(manifest_path, manifest)
        return result

    try:
        previous = None
        if method == 'incremental':
            for index in range(len(reports)):
                previous = step(f'induct-{index + 1:04d}', reports[:index + 1], previous,
                                f'Incorporate defect {reports[index]["defect_id"]} into the current catalog. Revise or add patterns as needed. Return the complete catalog for all supplied reports.')
        else:
            eligible = [r for r in reports if r['quality']['synthesis_eligibility'] == 'eligible']
            groups_path = root / 'groups.json'
            if resume and groups_path.exists():
                if digest(groups_path.read_bytes()) != manifest.get('groups_sha256'):
                    raise ValueError('Embedding proposals changed')
                groups = read_json(groups_path)
            else:
                groups = (grouper or embedding_groups)(eligible, embedding_model, embedding_revision, threshold, root / 'embeddings') if eligible else []
                flattened = [d for group in groups for d in group]
                if len(flattened) != len(set(flattened)) or set(flattened) != {r['defect_id'] for r in eligible}:
                    raise ValueError('Embedding proposals must partition the eligible inputs')
                write_json(groups_path, groups)
                manifest['groups_sha256'] = digest(groups_path.read_bytes())
                write_json(manifest_path, manifest)
            previous = []
            for index, group in enumerate(groups, 1):
                subset = [r for r in reports if r['defect_id'] in group]
                previous.append(step(f'group-{index:04d}', subset, None,
                                     f'Synthesize and verify patterns within this proposed group. Prefix pattern IDs with g{index:04d}-. Split or reject incoherent groups.'))
        catalog = step('reconcile', reports, previous,
                       'Reconcile the entire catalog across all input reports and proposal groups. Merge equivalent patterns, split incoherent patterns, re-evaluate all affected memberships, and preserve valid singleton candidates. Return the final complete catalog and accumulated decision history.')
        usages = [read_json(p) for p in sorted((root / 'calls').glob('*.usage.json'))]
        catalog['provenance'] = provenance(manifest['run_id'], corpus_hash, [i['sha256'] for i in inputs], model, PROMPT, time.monotonic() - started, usages)
        validate_catalog(catalog, reports, root)
        write_json(root / 'catalog.json', catalog)
        write(root / 'catalog.md', catalog_markdown(catalog))
        write(root / 'agent-guide.md', agent_guide(catalog))
        manifest.update(status='complete', finished_at=now(), elapsed_seconds=earlier_elapsed + time.monotonic() - started, catalog_sha256=digest((root / 'catalog.json').read_bytes()))
    except Exception as error:
        manifest.update(status='failed', finished_at=now(), elapsed_seconds=earlier_elapsed + time.monotonic() - started, error=str(error))
        write_json(manifest_path, manifest)
        raise
    write_json(manifest_path, manifest)
    return manifest

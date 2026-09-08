"""Corpus ingestion and comprehensive micro-analysis orchestration."""
from __future__ import annotations

import time
from pathlib import Path

from .artifacts import ROOT, content_hash, digest, encode, environment, inside, now, provenance, read_json, write, write_json
from .contracts import expanded_schema, schema, validate_micro
from .evidence import collect, load_corpus
from .models import request
from .render import micro_markdown

ANALYSIS_FIELDS = ['relationships', 'context', 'preconditions', 'causal_trace', 'violated_invariant', 'root_cause', 'existing_protections', 'consequence', 'fix', 'reproduction', 'mechanism_signature', 'quality']
PROMPT = (ROOT / 'prompts/micro.md').read_text()


def verify_bundle(bundle, root):
    for doc in bundle['documents']:
        raw = inside(root, doc['evidence']['artifact_path']).read_bytes()
        if digest(raw) != doc['evidence']['sha256']:
            raise ValueError('Archived evidence changed; start a new run')
        if doc['text'] and doc['text'].encode('utf-8') != raw:
            raise ValueError('Bundle text differs from archived evidence')


def run_micro(input_path, output, model, *, evidence_dir=None, resume=False, limit=None, attempts=2, max_prompt_chars=750_000, client=None, collect_only=False):
    root = Path(output)
    corpus = load_corpus(input_path)
    if limit is not None:
        if limit < 1:
            raise ValueError('limit must be positive')
        corpus['bugs'] = corpus['bugs'][:limit]
    env = environment()
    config = {'corpus': corpus, 'model': model.name, 'model_settings': model.settings,
              'implementation_sha256': env['implementation_sha256'], 'packages': env['packages'], 'attempts': attempts,
              'max_prompt_chars': max_prompt_chars, 'offline': evidence_dir is not None,
              'local_inputs': {str(Path(evidence_dir) / f'{b["defect_id"]}.json'): digest((Path(evidence_dir) / f'{b["defect_id"]}.json').read_bytes()) for b in corpus['bugs']} if evidence_dir else {}}
    for bug in corpus['bugs']:
        for log in bug.get('sanitizer_logs', []):
            config['local_inputs'][log['path']] = digest(Path(log['path']).read_bytes())
    run_path = root / 'run.json'
    if run_path.exists():
        manifest = read_json(run_path)
        if not resume:
            raise ValueError('Output already contains a run; use --resume or a new output directory')
        if manifest['config_sha256'] != content_hash(config):
            raise ValueError('Run inputs/configuration changed; use a new output directory')
        if manifest['status'] == 'complete':
            for item in manifest['items'].values():
                path = inside(root, item['report_path'])
                if digest(path.read_bytes()) != item['report_sha256']:
                    raise ValueError('Completed report changed')
                report = validate_micro(read_json(path), root)
                write(path.with_suffix('.md'), micro_markdown(report))
            return manifest
    else:
        if root.exists() and any(root.iterdir()):
            raise ValueError('New output directory must be empty')
        manifest = {'run_id': 'micro-' + content_hash(config)[:16], 'started_at': now(), 'config_sha256': content_hash(config),
                    'config': config, 'environment': env, 'status': 'running', 'items': {}}
        write_json(root / 'corpus.json', corpus)
    manifest['status'] = 'running'
    write_json(run_path, manifest)
    report_schema = schema('micro-report')
    analysis_schema = {'type': 'object', 'properties': {k: report_schema['properties'][k] for k in ANALYSIS_FIELDS}, 'required': ANALYSIS_FIELDS, 'additionalProperties': False}
    corpus_hash = content_hash(corpus)
    for bug in corpus['bugs']:
        identifier = bug['defect_id']
        report_path = root / 'reports' / f'{identifier}.json'
        previous = manifest['items'].get(identifier, {})
        if resume and previous.get('status') == 'complete':
            report = read_json(report_path)
            if digest(report_path.read_bytes()) != previous['report_sha256']:
                raise ValueError(f'Completed report changed: {identifier}')
            validate_micro(report, root)
            write(report_path.with_suffix('.md'), micro_markdown(report))
            continue
        started = time.monotonic()
        manifest['items'][identifier] = {**previous, 'status': 'running'}
        write_json(run_path, manifest)
        print(f'Micro: {identifier}', flush=True)
        try:
            bundle_path = root / 'bundles' / f'{identifier}.json'
            if resume and bundle_path.exists() and previous.get('bundle_sha256') and digest(bundle_path.read_bytes()) != previous['bundle_sha256']:
                raise ValueError('Evidence bundle changed; start a new run')
            bundle = read_json(bundle_path) if resume and bundle_path.exists() else collect(bug, root, client, evidence_dir)
            verify_bundle(bundle, root)
            manifest['items'][identifier]['bundle_sha256'] = digest(bundle_path.read_bytes())
            write_json(run_path, manifest)
            if collect_only:
                manifest['items'][identifier]['status'] = 'collected'
                write_json(run_path, manifest)
                continue
            hashes = [content_hash(bundle)]
            def finalize(analysis):
                if set(analysis) != set(ANALYSIS_FIELDS):
                    raise ValueError('Response must contain exactly the requested analysis fields')
                # No model may rewrite source-derived metadata or assert execution by this stage.
                if analysis['reproduction']['status'] != 'not_attempted':
                    raise ValueError('This stage does not run reproducers; status must be not_attempted')
                if analysis['reproduction']['input_artifact'] is not None:
                    allowed = {d['evidence']['artifact_path'] for d in bundle['documents'] if d['evidence']['id'] in bundle.get('reproducer_candidates', [])}
                    if analysis['reproduction']['input_artifact'] not in allowed:
                        raise ValueError('input_artifact must be null or an archived reproducer candidate path from the bundle')
                quality = analysis['quality']
                for warning in bundle['warnings']:
                    if warning not in quality['validation_findings']:
                        quality['validation_findings'].append(warning)
                if bundle['sanitizer_output']['status'] in ('partial', 'unavailable'):
                    warning = 'Full sanitizer output requirement is unmet; sanitizer-based deduplication is incomplete.'
                    if warning not in quality['validation_findings']:
                        quality['validation_findings'].append(warning)
                report = {'schema_version': '0.1.0', 'defect_id': identifier, 'report_version': 1,
                          'issue_urls': bug['issues'], 'issue_states': [{'url': i['url'], 'state': i['state']} for i in bundle['issues']],
                          'evidence': [d['evidence'] for d in bundle['documents']], 'sanitizer_output': bundle['sanitizer_output'],
                          **analysis, 'provenance': provenance(manifest['run_id'], corpus_hash, hashes, model, PROMPT, time.monotonic() - started, [])}
                return validate_micro(report, root)
            # Diagnostics remain verbatim in their evidence documents. Avoid sending
            # a second copy of every log inside the deterministic output metadata.
            prompt_bundle = {**bundle, 'sanitizer_output': {**bundle['sanitizer_output'], 'outputs': [{k: v for k, v in o.items() if k != 'raw_output'} for o in bundle['sanitizer_output']['outputs']]}}
            prompt = PROMPT + '\nAnalysis schema:\n' + encode(expanded_schema(analysis_schema)) + '\nCanonical defect:\n' + encode(bug) + '\nEvidence bundle (full diagnostics in document text):\n' + encode(prompt_bundle)
            if len(prompt) > max_prompt_chars:
                raise ValueError(f'Prompt has {len(prompt)} characters, limit is {max_prompt_chars}. Evidence retained; raise --max-prompt-chars after checking model context limits.')
            report = request(model, f'micro-{identifier}', prompt, root / 'calls', finalize, attempts, max_prompt_chars=max_prompt_chars)
            usages = [read_json(p) for p in sorted((root / 'calls').glob(f'micro-{identifier}.*.usage.json'))]
            report['provenance'] = provenance(manifest['run_id'], corpus_hash, hashes, model, PROMPT, time.monotonic() - started, usages)
            write_json(report_path, report)
            write(report_path.with_suffix('.md'), micro_markdown(report))
            write_json(root / 'signatures' / f'{identifier}.json', report['mechanism_signature'])
            manifest['items'][identifier] = {**manifest['items'][identifier], 'status': 'complete', 'report_sha256': digest(report_path.read_bytes()), 'report_path': str(report_path.relative_to(root)),
                                             'sanitizer_status': report['sanitizer_output']['status'], 'elapsed_seconds': time.monotonic() - started}
        except Exception as error:
            manifest['items'][identifier] = {**manifest['items'][identifier], 'status': 'failed', 'error': str(error), 'elapsed_seconds': time.monotonic() - started}
            print(f'  Failed: {error}', flush=True)
        write_json(run_path, manifest)
    expected = ('complete', 'collected') if collect_only else ('complete',)
    manifest['status'] = ('evidence_collected' if collect_only else 'complete') if all(v['status'] in expected for v in manifest['items'].values()) else 'partial_failure'
    manifest['finished_at'] = now()
    write_json(run_path, manifest)
    return manifest

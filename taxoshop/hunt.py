"""Bounded source-snapshot search with evidence-only models and frozen inputs."""
from __future__ import annotations

import subprocess
import time
from pathlib import Path, PurePosixPath

from .artifacts import ROOT, content_hash, digest, encode, environment, inside, now, provenance, read_json, write, write_json
from .contracts import expanded_schema, schema, unique, validate_catalog, validate_micro, validate_schema
from .macro import load_reports
from .models import request
from .render import agent_guide, micro_markdown, render_value

PROMPT = (ROOT / 'prompts/hunt.md').read_text()


def git(repo, *args):
    result = subprocess.run(['git', '--literal-pathspecs', '-C', str(repo), *args], capture_output=True)
    if result.returncode:
        raise ValueError('Cannot read pinned target: ' + result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout


def snapshot(repo, revision, paths, max_bytes):
    """Read only committed regular blobs; the working tree is never searched."""
    import re
    if not re.fullmatch(r'[a-f0-9]{40}', revision):
        raise ValueError('Target revision must be a full lowercase commit SHA')
    if git(repo, 'rev-parse', '--verify', revision + '^{commit}').decode().strip() != revision:
        raise ValueError('Target revision must identify a commit, not a tag object')
    if not paths or len(paths) != len(set(paths)) or max_bytes < 1:
        raise ValueError('Supply unique source files and a positive source byte budget')
    documents = []
    total = 0
    for path in sorted(paths):
        relative = PurePosixPath(path)
        if relative.is_absolute() or any(p in ('..', '.') for p in path.split('/')) or str(relative) != path or '\\' in path:
            raise ValueError('Source paths must be canonical repository-relative paths')
        entries = git(repo, 'ls-tree', '-z', revision, '--', path).split(b'\0')
        if len(entries) != 2 or not entries[0]:
            raise ValueError(f'Source file absent from target revision: {path}')
        metadata, name = entries[0].split(b'\t', 1)
        mode, kind, oid = metadata.decode().split()
        if name.decode('utf-8') != path or mode not in ('100644', '100755') or kind != 'blob':
            raise ValueError(f'Source must be a regular committed file: {path}')
        size = int(git(repo, 'cat-file', '-s', oid))
        total += size
        if total > max_bytes:
            raise ValueError('Selected source exceeds --max-source-bytes; no files silently truncated')
        raw = git(repo, 'cat-file', 'blob', oid)
        if b'\0' in raw:
            raise ValueError(f'Binary source is unsupported: {path}')
        text = raw.decode('utf-8')
        documents.append({'path': path, 'artifact_path': 'source/' + path, 'sha256': digest(raw),
                          'lines': len(text.splitlines()), 'text': text})
    return documents


def documentation(condition, input_dir, split_path, partition):
    if condition == 'none':
        if input_dir is not None:
            raise ValueError('The none condition does not accept documentation inputs')
        return '', [], [], None, None, {}
    if condition not in ('micro', 'incremental', 'embedding') or input_dir is None or split_path is None:
        raise ValueError('Corpus-derived conditions require --input and --split')
    if partition not in ('discovery', 'development'):
        raise ValueError('Documentation must come from discovery or development')
    from .evaluation import validate_split
    split = validate_split(read_json(split_path))
    allowed = {r['defect_id']: r for r in split['reports'] if r['partition'] == partition}
    directory = Path(input_dir)
    catalog = None
    if condition == 'micro':
        # A split may be created from the full micro run; only selected members
        # reach the searching model. All available reports still validate first.
        loaded = [(r, p) for r, p in load_reports(directory) if r['defect_id'] in allowed]
        text = '\n\n'.join(micro_markdown(r) for r, _ in loaded)
        patterns = []
    else:
        manifest = read_json(directory / 'run.json')
        path = directory / 'catalog.json'
        if manifest['status'] != 'complete' or digest(path.read_bytes()) != manifest['catalog_sha256']:
            raise ValueError('Catalog must come from an intact completed run')
        catalog = read_json(path)
        if catalog['method'] != condition:
            raise ValueError('Catalog method differs from experimental condition')
        loaded = [(read_json(inside(directory, i['artifact_path'])), inside(directory, i['artifact_path'])) for i in catalog['input_reports']]
        for report, _ in loaded:
            validate_micro(report, directory / 'inputs')
        validate_catalog(catalog, [r for r, _ in loaded], directory)
        patterns = [p for p in catalog['patterns'] if p['status'] != 'retired']
        text = agent_guide(catalog) + '\nMachine-readable pattern predicates:\n' + encode(patterns)
    if not loaded:
        raise ValueError('No documentation reports in the requested partition')
    inputs, archive = [], {}
    for report, path in loaded:
        identifier = report['defect_id']
        if identifier not in allowed:
            raise ValueError('Documentation leaks a defect outside the selected partition')
        sha = digest(path.read_bytes())
        if sha != allowed[identifier]['sha256']:
            raise ValueError('Documentation report differs from frozen split')
        inputs.append({'defect_id': identifier, 'sha256': sha})
        archive[f'inputs/reports/{identifier}.json'] = path.read_bytes()
        evidence_root = directory if condition == 'micro' else directory / 'inputs'
        for item in report['evidence']:
            relative = str(inside(evidence_root, item['artifact_path']).relative_to(evidence_root.resolve()))
            archive['inputs/' + relative] = inside(evidence_root, item['artifact_path']).read_bytes()
    return text, patterns, inputs, split, catalog, archive


def validate_hunt(report, root=None, patterns=None):
    validate_schema(report, 'hunt-report')
    files = unique(report['source_manifest'], 'path', 'source path')
    texts = {}
    if root is not None:
        for path, item in files.items():
            raw = inside(root, item['artifact_path']).read_bytes()
            if digest(raw) != item['sha256']:
                raise ValueError('Source snapshot hash mismatch')
            texts[path] = raw.decode('utf-8').splitlines()
            if len(texts[path]) != item['lines']:
                raise ValueError('Source line count mismatch')
        raw = (Path(root) / 'documentation.md').read_bytes()
        if digest(raw) != report['documentation_sha256'] or len(raw.decode('utf-8')) != report['documentation_characters']:
            raise ValueError('Documentation hash or length mismatch')
        if patterns is None:
            patterns = read_json(Path(root) / 'patterns.json')
    pattern_map = unique(patterns or [], 'pattern_id', 'pattern ID')
    if patterns is not None and set(pattern_map) != set(report['pattern_ids']):
        raise ValueError('Pattern index differs from frozen documentation')
    unique(report['findings'], 'finding_id', 'finding ID')

    def refs(references):
        for ref in references:
            item = files.get(ref['path'])
            if item is None or not 1 <= ref['start_line'] <= ref['end_line'] <= item['lines']:
                raise ValueError('Finding references an unknown source or invalid line range')
            if texts and ref['quote'] != '\n'.join(texts[ref['path']][ref['start_line'] - 1:ref['end_line']]):
                raise ValueError('Finding quote must equal the cited complete source lines')

    for finding in report['findings']:
        refs(finding['source_refs'])
        assessments = unique(finding['pattern_assessments'], 'pattern_id', 'pattern assessment')
        if not set(assessments) <= set(report['pattern_ids']):
            raise ValueError('Finding cites a pattern absent from supplied documentation')
        for pid, assessment in assessments.items():
            checks = unique(assessment['condition_checks'], 'condition_id', 'condition check')
            if patterns is not None:
                expected = {c['id'] for c in pattern_map[pid]['membership_conditions'] + pattern_map[pid]['exclusion_conditions']}
                if set(checks) != expected:
                    raise ValueError('Pattern assessment must check every membership and exclusion condition')
            for check in checks.values():
                if check['outcome'] != 'unknown' and not check['source_refs']:
                    raise ValueError('Known predicate outcomes require source references')
                refs(check['source_refs'])
    return report


def load_hunt(root, allow_failed=False):
    root = Path(root)
    manifest = read_json(root / 'run.json')
    if manifest.get('stage') != 'hunt' or content_hash(manifest['config']) != manifest['config_sha256']:
        raise ValueError('Invalid hunt manifest configuration')
    for path, sha in manifest['artifacts'].items():
        if digest(inside(root, path).read_bytes()) != sha:
            raise ValueError(f'Hunt artifact changed: {path}')
    if manifest['status'] != 'complete':
        if allow_failed and manifest['status'] in ('failed', 'running'):
            return manifest, None
        raise ValueError('Hunt run is incomplete')
    path = root / 'findings.json'
    if digest(path.read_bytes()) != manifest['report_sha256']:
        raise ValueError('Completed hunt report changed')
    report = validate_hunt(read_json(path), root)
    config = manifest['config']
    if (report['hunt_id'] != manifest['run_id'] or report['condition'] != config['condition']
            or report['target_revision'] != config['target_revision'] or report['source_manifest'] != config['sources']
            or report['documentation_sha256'] != config['documentation_sha256']):
        raise ValueError('Hunt report differs from run configuration')
    return manifest, report


def run_hunt(repo, revision, paths, output, model, *, condition='none', input_dir=None, split_path=None,
             partition='discovery', resume=False, attempts=2, max_prompt_chars=750000,
             max_source_bytes=500000, max_documentation_chars=100000, max_findings=20, seed=0):
    if min(attempts, max_prompt_chars, max_source_bytes, max_findings) < 1 or max_documentation_chars < 0:
        raise ValueError('Budgets must be positive (documentation may be zero)')
    sources = snapshot(repo, revision, paths, max_source_bytes)
    doc, patterns, inputs, split, catalog, input_artifacts = documentation(condition, input_dir, split_path, partition)
    if len(doc) > max_documentation_chars:
        raise ValueError('Documentation exceeds --max-documentation-chars; select a smaller frozen corpus')
    env = environment()
    config = {'condition': condition, 'target_revision': revision, 'sources': [{k: v for k, v in s.items() if k != 'text'} for s in sources],
              'documentation_sha256': digest(doc), 'documentation_inputs': inputs,
              'split_sha256': content_hash(split) if split else None, 'partition': partition if split else None,
              'catalog_sha256': content_hash(catalog) if catalog else None,
              'model': model.name, 'model_settings': model.settings, 'seed': seed,
              'attempts': attempts, 'max_prompt_chars': max_prompt_chars, 'max_source_bytes': max_source_bytes,
              'max_documentation_chars': max_documentation_chars, 'max_findings': max_findings,
              'implementation_sha256': env['implementation_sha256'], 'packages': env['packages'],
              'search_policy': 'complete-selected-source-snapshot-v1'}
    root = Path(output)
    run_path = root / 'run.json'
    if run_path.exists():
        manifest, report = load_hunt(root, allow_failed=True)
        if not resume or manifest['config_sha256'] != content_hash(config):
            raise ValueError('Existing hunt requires --resume with identical inputs and configuration')
        if report is not None:
            return manifest
    else:
        if root.exists() and any(root.iterdir()):
            raise ValueError('New output directory must be empty')
        manifest = {'stage': 'hunt', 'run_id': 'hunt-' + content_hash(config)[:16], 'config': config,
                    'config_sha256': content_hash(config), 'environment': env, 'started_at': now(), 'artifacts': {}}
        for source in sources:
            write(inside(root, source['artifact_path']), source['text'])
        write(root / 'documentation.md', doc)
        write_json(root / 'patterns.json', patterns)
        if split:
            write_json(root / 'split.json', split)
        if catalog:
            write_json(root / 'catalog.json', catalog)
        for path, raw in input_artifacts.items():
            write(inside(root, path), raw)
        archived = [s['artifact_path'] for s in sources] + ['documentation.md', 'patterns.json']
        archived += (['split.json'] if split else []) + (['catalog.json'] if catalog else [])
        archived += list(input_artifacts)
        manifest['artifacts'] = {p: digest(inside(root, p).read_bytes()) for p in archived}
    manifest.update(status='running')
    manifest.pop('error', None)
    write_json(run_path, manifest)
    started = time.monotonic()
    try:
        prompt = (PROMPT + '\nResponse schema:\n' + encode(expanded_schema(schema('hunt-response')))
                  + '\nCondition: ' + condition + '\nTarget revision: ' + revision
                  + '\nMaximum findings: ' + str(max_findings) + '\nRun label seed: ' + str(seed)
                  + '\nDocumentation:\n' + doc
                  + '\nComplete selected source files:\n' + encode([{'path': s['path'], 'text': s['text']} for s in sources]))
        def finalize(data):
            validate_schema(data, 'hunt-response')
            if len(data['findings']) > max_findings:
                raise ValueError('Response exceeds configured maximum findings')
            report = {'schema_version': '0.1.0', 'hunt_id': manifest['run_id'], 'condition': condition,
                      'target_revision': revision, 'source_manifest': config['sources'], 'documentation_sha256': digest(doc),
                      'documentation_characters': len(doc), 'pattern_ids': [p['pattern_id'] for p in patterns], **data,
                      'provenance': provenance(manifest['run_id'], content_hash(inputs), [content_hash(config)], model, PROMPT, time.monotonic() - started, [])}
            return validate_hunt(report, root, patterns)
        report = request(model, 'hunt', prompt, root / 'calls', finalize, attempts, max_prompt_chars=max_prompt_chars)
        usages = [read_json(p) for p in sorted((root / 'calls').glob('*.usage.json'))]
        report['provenance'] = provenance(manifest['run_id'], content_hash(inputs), [content_hash(config)], model, PROMPT, time.monotonic() - started, usages)
        write_json(root / 'findings.json', report)
        write(root / 'findings.md', '# Candidate findings\n\nThese are unvalidated hypotheses; proposed tests were not executed.\n\n' + render_value(report))
        manifest.update(status='complete', report_sha256=digest((root / 'findings.json').read_bytes()))
    except Exception as error:
        manifest.update(status='failed', error=str(error))
        raise
    finally:
        manifest['elapsed_seconds'] = manifest.get('elapsed_seconds', 0) + time.monotonic() - started
        manifest['finished_at'] = now()
        write_json(run_path, manifest)
    return manifest

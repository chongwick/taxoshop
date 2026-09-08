"""Deterministic artifacts, content hashes, and run provenance."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import tempfile
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def digest(value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    return hashlib.sha256(value).hexdigest()


def encode(value):
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n'


def content_hash(value):
    return digest(encode(value))


def read_json(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, bytes) else value.encode('utf-8')
    fd, temp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        Path(temp).replace(path)
    finally:
        Path(temp).unlink(missing_ok=True)


def write_json(path, value):
    write(path, encode(value))


def inside(root, relative):
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError(f'Artifact path escapes run directory: {relative}')
    return path


def implementation_hash():
    paths = sorted([*ROOT.joinpath('taxoshop').glob('*.py'), *ROOT.joinpath('schemas').glob('*.json'), *ROOT.joinpath('prompts').glob('*.md')])
    return content_hash({str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in paths})


def environment():
    packages = {}
    for name in ['openai-codex', 'openai-codex-cli-bin', 'pydantic', 'jsonschema', 'referencing', 'jsonschema-specifications', 'rpds-py', 'sentence-transformers', 'transformers', 'torch', 'scikit-learn', 'numpy', 'scipy']:
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            pass
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, capture_output=True)
    return {'python': platform.python_version(), 'platform': platform.platform(), 'packages': packages,
            'git_revision': result.stdout.strip() if result.returncode == 0 else None,
            'implementation_sha256': implementation_hash()}


def provenance(run_id, corpus_hash, hashes, model, prompt, elapsed, calls):
    def total(field):
        values = [c.get(field) for c in calls]
        return sum(values) if values and all(v is not None for v in values) else None
    return {'run_id': run_id, 'created_at': now(), 'corpus_manifest_sha256': corpus_hash,
            'input_artifact_sha256s': hashes, 'prompt_version': digest(prompt), 'model': model.name,
            'settings': model.settings, 'elapsed_seconds': elapsed,
            'input_tokens': total('input_tokens'), 'output_tokens': total('output_tokens')}

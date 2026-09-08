"""Embedding proposals from causal signatures, never complete Markdown reports."""
from __future__ import annotations

import math
import re
from pathlib import Path

from .artifacts import content_hash, read_json, write_json

SIGNATURE_VERSION = 'causal-fields-v1'
SIGNATURE_FIELDS = ('context', 'preconditions', 'invariant', 'causal_mechanism', 'consequence', 'repair_principle')


def signature_text(report):
    return '\n'.join(f'{key}: {report["mechanism_signature"][key]["statement"]}' for key in SIGNATURE_FIELDS if report['mechanism_signature'][key]['basis'] != 'unknown')


def cluster_vectors(vectors, threshold):
    if not 0 <= threshold <= 2 or not math.isfinite(threshold):
        raise ValueError('Cosine distance threshold must be between 0 and 2')
    if not vectors:
        return []
    dimension = len(vectors[0])
    for vector in vectors:
        if not dimension or len(vector) != dimension or not all(math.isfinite(x) for x in vector) or sum(x*x for x in vector) == 0:
            raise ValueError('Embeddings must be finite, nonzero, and have consistent dimensions')
    if len(vectors) == 1:
        return [0]
    from sklearn.cluster import AgglomerativeClustering
    return [int(v) for v in AgglomerativeClustering(n_clusters=None, metric='cosine', linkage='average', distance_threshold=threshold).fit_predict(vectors)]


def embedding_groups(reports, model_name, revision, threshold, cache_dir):
    if not revision or not re.fullmatch(r'[0-9a-fA-F]{40}', revision):
        raise ValueError('Embedding runs require an explicit full commit SHA for --embedding-revision')
    from sentence_transformers import SentenceTransformer
    cache = Path(cache_dir)
    vectors, model = [], None
    for report in reports:
        text = signature_text(report)
        if not text:
            raise ValueError(f'No known mechanism signature for {report["defect_id"]}; exclude it from embedding proposals explicitly')
        from importlib.metadata import version
        runtime = {name: version(name) for name in ('sentence-transformers', 'transformers', 'torch', 'numpy')}
        key = content_hash({'model': model_name, 'revision': revision, 'runtime': runtime, 'device': 'cpu', 'serialization': SIGNATURE_VERSION, 'text': text})
        path = cache / f'{key}.json'
        if path.exists():
            entry = read_json(path)
            if entry['key'] != key:
                raise ValueError('Embedding cache key mismatch')
            if content_hash(entry['vector']) != entry['vector_sha256']:
                raise ValueError('Embedding cache vector hash mismatch')
            vector = entry['vector']
        else:
            if model is None:
                model = SentenceTransformer(model_name, revision=revision, trust_remote_code=False, device='cpu')
            token_count = len(model.tokenizer.encode(text, add_special_tokens=True, truncation=False))
            if token_count > model.max_seq_length:
                raise ValueError(f'Signature for {report["defect_id"]} exceeds embedding model token limit ({token_count} > {model.max_seq_length}); shorten the signature instead of silently truncating')
            vector = model.encode([text], normalize_embeddings=True)[0].tolist()
            write_json(path, {'key': key, 'text': text, 'vector': vector, 'vector_sha256': content_hash(vector)})
        vectors.append(vector)
    labels = cluster_vectors(vectors, threshold)
    groups = {}
    for report, group in zip(reports, labels):
        groups.setdefault(group, []).append(report['defect_id'])
    return list(groups.values())

"""Cluster similar bug fingerprints from taxos/micro_taxo.

Each *.md file is a "micro taxonomy" describing one bug. We embed each file,
group similar bugs with agglomerative clustering, and emit the clusters as
JSON (and optionally a 2D scatter plot).

Embeddings are cached per-file by content hash, so reruns only re-encode files
that were added or changed.

Usage:
    python cluster.py                         # cluster with defaults
    python cluster.py --threshold 0.4         # tighter/looser clusters
    python cluster.py --no-cache              # ignore the embedding cache
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
INPUT_DIR = Path("taxos/micro_taxo")
CACHE_PATH = Path("embeddings_cache.npz")
OUTPUT_PATH = Path("clusters.json")


def load_bug_fingerprints(input_dir):
    """Return (names, texts) for every *.md fingerprint, sorted by name."""
    names, texts = [], []
    for path in sorted(input_dir.glob("*.md")):
        names.append(path.name)
        texts.append(path.read_text())
    return names, texts


def _content_key(text):
    """Stable cache key for a fingerprint's text (model-specific)."""
    h = hashlib.sha256()
    h.update(MODEL_NAME.encode())
    h.update(b"\0")
    h.update(text.encode())
    return h.hexdigest()


def load_cache(cache_path):
    """Load {content_key: embedding} from an .npz cache, or {} if absent."""
    if not cache_path.exists():
        return {}
    data = np.load(cache_path, allow_pickle=True)
    return dict(zip(data["keys"], data["embeddings"]))


def save_cache(cache_path, cache):
    keys = np.array(list(cache.keys()))
    embeddings = np.array(list(cache.values()))
    np.savez(cache_path, keys=keys, embeddings=embeddings)


def get_embeddings(texts, model, cache_path, use_cache=True):
    """Embed texts, reusing cached vectors for unchanged content.

    Only files whose content hash is missing from the cache are re-encoded.
    """
    cache = load_cache(cache_path) if use_cache else {}
    keys = [_content_key(t) for t in texts]

    missing = [(i, t) for i, (t, k) in enumerate(zip(texts, keys)) if k not in cache]
    if missing:
        print(f"Encoding {len(missing)} new/changed fingerprint(s)...")
        new_vecs = model.encode(
            [t for _, t in missing],
            normalize_embeddings=True,
        )
        for (i, _), vec in zip(missing, new_vecs):
            cache[keys[i]] = vec
    else:
        print("All fingerprints served from cache.")

    if use_cache:
        save_cache(cache_path, cache)

    return np.array([cache[k] for k in keys])


def cluster_embeddings(embeddings, threshold):
    """Agglomerative clustering on cosine distance with a distance threshold.

    No fixed number of clusters: anything closer than `threshold` in cosine
    distance gets merged. Returns an array of integer cluster labels.
    """
    model = AgglomerativeClustering(
        n_clusters=None,
        metric="cosine",
        linkage="average",
        distance_threshold=threshold,
    )
    return model.fit_predict(embeddings)


def group_by_cluster(names, labels):
    """Return {cluster_id: [names...]}, largest clusters first."""
    clusters = {}
    for name, label in zip(names, labels):
        clusters.setdefault(int(label), []).append(name)
    return dict(sorted(clusters.items(), key=lambda kv: (-len(kv[1]), kv[0])))


def report(clusters):
    """Print clusters to stdout, singletons summarized at the end."""
    multi = {cid: members for cid, members in clusters.items() if len(members) > 1}
    singletons = [m[0] for m in clusters.values() if len(m) == 1]

    print(f"\n{len(clusters)} clusters "
          f"({len(multi)} with >1 member, {len(singletons)} singletons)\n")
    for cid, members in multi.items():
        print(f"Cluster {cid} ({len(members)} bugs):")
        for name in members:
            print(f"    {name}")
        print()
    if singletons:
        print(f"Singletons ({len(singletons)}): {', '.join(singletons)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--threshold", type=float, default=0.15,
                        help="cosine distance merge threshold (default: 0.15; "
                             "lower = tighter clusters). These fingerprints "
                             "share a markdown template so distances are small.")
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--cache", type=Path, default=CACHE_PATH)
    parser.add_argument("--no-cache", action="store_true",
                        help="ignore and don't update the embedding cache")
    args = parser.parse_args()

    names, texts = load_bug_fingerprints(args.input_dir)
    if not names:
        print(f"No *.md files found in {args.input_dir}")
        return
    print(f"Loaded {len(names)} bug fingerprints from {args.input_dir}")

    model = SentenceTransformer(MODEL_NAME)
    embeddings = get_embeddings(texts, model, args.cache, use_cache=not args.no_cache)

    labels = cluster_embeddings(embeddings, args.threshold)
    clusters = group_by_cluster(names, labels)
    report(clusters)

    args.output.write_text(json.dumps(clusters, indent=2))
    print(f"\nWrote clusters to {args.output}")


if __name__ == "__main__":
    main()

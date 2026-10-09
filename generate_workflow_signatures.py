#!/usr/bin/env python3
"""Generate abstract bug workflows, then cluster them with local embeddings.

Codex creates one implementation-neutral workflow for each detailed report. A
separate CPU-only pass embeds every saved workflow with sentence-transformers
and forms clusters from cosine similarity; the LLM never decides clustering.

Requires Python 3.10+, ``pip install openai-codex sentence-transformers`` and
an authenticated Codex installation. The embedding model downloads once, then
sentence-transformers uses its local cache.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPOSITORY = Path(__file__).resolve().parent
REPORTS = REPOSITORY / "taxos" / "micro_taxo"
OUTPUT = REPOSITORY / "taxos" / "workflow_signatures"
SIGNATURES = OUTPUT
CLUSTERS_PATH = OUTPUT / "clusters.json"
REPORT_NUMBER = re.compile(r"gh_(\d+)\.md$")
CORPORA = {
    "cpython": {"reports": REPOSITORY / "taxos" / "micro_taxo", "output": REPOSITORY / "taxos" / "workflow_signatures", "report_pattern": re.compile(r"gh_(\d+)\.md$"), "report_glob": "gh_*.md", "signature_prefix": "gh"},
    "ruby": {"reports": REPOSITORY / "taxos" / "ruby_micro_taxo", "output": REPOSITORY / "taxos" / "ruby_workflow_signatures", "report_pattern": re.compile(r"ruby_(\d+)\.md$"), "report_glob": "ruby_*.md", "signature_prefix": "ruby"},
}
OUTPUT_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["workflow", "summary"], "properties": {
    "workflow": {"type": "array", "minItems": 2, "maxItems": 8, "items": {"type": "string", "minLength": 8, "maxLength": 180}, "description": "Ordered, general workflow steps."},
    "summary": {"type": "string", "minLength": 16, "maxLength": 300, "description": "A concise, implementation-neutral workflow label."},
}}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", choices=CORPORA, default="cpython", help="micro-taxonomy corpus to process (default: cpython)")
    parser.add_argument("--model", default="gpt-5.6-terra", help="Codex model to use for workflow generation")
    parser.add_argument("--embedding-model", default="all-MiniLM-L6-v2", help="sentence-transformers model used locally on CPU")
    parser.add_argument("--similarity-threshold", type=float, default=0.72, help="cosine-similarity edge threshold, in (0, 1] (default: 0.72)")
    parser.add_argument("--limit", type=int, help="process at most this many unprocessed reports")
    parser.add_argument("--only", nargs="+", type=int, metavar="ISSUE", help="process only these issue numbers")
    parser.add_argument("--force", action="store_true", help="regenerate workflows that already exist")
    parser.add_argument("--recluster-only", action="store_true", help="skip Codex and rebuild clusters from saved workflows")
    parser.add_argument("--clusters-output", type=Path, help="write embedding clusters to this path instead of the corpus default")
    parser.add_argument("--dry-run", action="store_true", help="show reports that would be generated and the clustering settings")
    args = parser.parse_args()
    if not 0 < args.similarity_threshold <= 1:
        parser.error("--similarity-threshold must be greater than 0 and no greater than 1")
    if args.recluster_only and (args.force or args.only or args.limit):
        parser.error("--recluster-only cannot be combined with --force, --only, or --limit")
    return args


def configure_corpus(name: str) -> None:
    global REPORTS, OUTPUT, SIGNATURES, CLUSTERS_PATH, REPORT_NUMBER
    corpus = CORPORA[name]
    REPORTS, OUTPUT = corpus["reports"], corpus["output"]
    SIGNATURES, CLUSTERS_PATH, REPORT_NUMBER = OUTPUT, OUTPUT / "clusters.json", corpus["report_pattern"]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def issue_number(path: Path) -> int:
    match = REPORT_NUMBER.search(path.name)
    if not match:
        raise ValueError(f"Unexpected report name: {path.name}")
    return int(match.group(1))


def reports_to_process(args: argparse.Namespace) -> list[Path]:
    corpus = CORPORA[args.corpus]
    reports = sorted(REPORTS.glob(corpus["report_glob"]), key=issue_number)
    if args.only:
        requested = set(args.only)
        reports = [path for path in reports if issue_number(path) in requested]
        missing = requested - {issue_number(path) for path in reports}
        if missing:
            raise ValueError(f"No rendered report for issue(s): {', '.join(map(str, sorted(missing)))}")
    if not args.force:
        prefix = corpus["signature_prefix"]
        reports = [path for path in reports if not (SIGNATURES / f"{prefix}_{issue_number(path)}.json").exists()]
    return reports[: args.limit] if args.limit else reports


def prompt_for(report: Path) -> str:
    return f"""Read the detailed bug analysis at `{report.relative_to(REPOSITORY)}`. Do not edit any files.

Create an abstract workflow signature that makes this bug comparable to bugs
from unrelated projects. Describe the causal sequence, not source-code
identifiers. Remove project-specific names, API names, test names, file names,
issue IDs, library names, platform releases, and implementation details whenever
an accurate general term exists. Preserve the bug mechanism and order.

For example, prefer 'a worker exits while shared state is being torn down' over
names of a runtime, class, test, or function. Do not merely restate the title.
A workflow must have 2–8 concise ordered steps.

Return only JSON matching the supplied schema."""


def parse_response(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S).strip()
    data = json.loads(text)
    if not isinstance(data, dict) or set(data) != set(OUTPUT_SCHEMA["required"]):
        raise ValueError("Codex response did not contain the expected fields")
    workflow = data["workflow"]
    if not isinstance(workflow, list) or not 2 <= len(workflow) <= 8 or not all(isinstance(step, str) and step.strip() for step in workflow):
        raise ValueError("Codex response contains an invalid workflow")
    if not isinstance(data["summary"], str) or not data["summary"].strip():
        raise ValueError("Codex response contains an empty summary")
    return {"workflow": [step.strip() for step in workflow], "summary": data["summary"].strip()}


def signature_record(number: int, signature: dict[str, Any], model: str) -> dict[str, Any]:
    return {"schema_version": 2, "issue": number, "workflow": signature["workflow"], "summary": signature["summary"], "model": model, "generated_at": datetime.now(timezone.utc).isoformat()}


def load_signatures(corpus: str) -> list[dict[str, Any]]:
    """Load v2 signatures and legacy v1 signatures during migration."""
    prefix = CORPORA[corpus]["signature_prefix"]
    signatures = []
    for path in sorted(SIGNATURES.glob(f"{prefix}_*.json")):
        data = json.loads(path.read_text())
        workflow = data.get("workflow")
        if not isinstance(data.get("issue"), int) or not isinstance(data.get("summary"), str) or not isinstance(workflow, list) or not workflow or not all(isinstance(step, str) and step.strip() for step in workflow):
            raise ValueError(f"Invalid workflow signature: {path}")
        signatures.append({"issue": data["issue"], "summary": data["summary"].strip(), "workflow": [step.strip() for step in workflow]})
    if len({signature["issue"] for signature in signatures}) != len(signatures):
        raise ValueError("Multiple signature files describe the same issue")
    return sorted(signatures, key=lambda signature: signature["issue"])


def embedding_text(signature: dict[str, Any]) -> str:
    return f"{signature['summary']}\n" + "\n".join(f"{index + 1}. {step}" for index, step in enumerate(signature["workflow"]))


def connected_components(embeddings: Any, threshold: float) -> list[list[int]]:
    """Cluster workflows joined by cosine-similarity edges, entirely locally."""
    parents = list(range(len(embeddings)))
    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index
    def union(left: int, right: int) -> None:
        left, right = find(left), find(right)
        if left != right:
            parents[right] = left
    similarities = embeddings @ embeddings.T  # encoder output is normalized
    for left in range(len(embeddings)):
        for right in range(left + 1, len(embeddings)):
            if float(similarities[left, right]) >= threshold:
                union(left, right)
    components: dict[int, list[int]] = defaultdict(list)
    for index in range(len(embeddings)):
        components[find(index)].append(index)
    return sorted(components.values(), key=lambda members: min(members))


def cluster_signatures(signatures: list[dict[str, Any]], model_name: str, threshold: float) -> dict[str, Any]:
    if not signatures:
        return {"schema_version": 1, "embedding_model": model_name, "similarity_threshold": threshold, "clusters": {}}
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError("Install local embedding support: pip install sentence-transformers") from exc
    model = SentenceTransformer(model_name, device="cpu")
    embeddings = model.encode([embedding_text(signature) for signature in signatures], convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=True)
    clusters: dict[str, dict[str, Any]] = {}
    for ordinal, members in enumerate(connected_components(embeddings, threshold), 1):
        # The medoid is a representative workflow for downstream taxonomy prompts.
        similarities = embeddings[members] @ embeddings[members].T
        representative = members[int(similarities.sum(axis=1).argmax())]
        clusters[f"workflow-{ordinal:04d}"] = {"summary": signatures[representative]["summary"], "workflow": signatures[representative]["workflow"], "issues": [signatures[index]["issue"] for index in members]}
    return {"schema_version": 1, "embedding_model": model_name, "similarity_threshold": threshold, "clusters": clusters}


def main() -> int:
    args = parse_args()
    configure_corpus(args.corpus)
    if args.clusters_output:
        global CLUSTERS_PATH
        CLUSTERS_PATH = args.clusters_output.resolve()
    reports = [] if args.recluster_only else reports_to_process(args)
    if args.dry_run:
        print("Would generate:", ", ".join(str(issue_number(path)) for path in reports) or "none")
        print(f"Would cluster all saved workflows with {args.embedding_model!r} at cosine similarity >= {args.similarity_threshold:g}.")
        return 0
    if reports:
        try:
            from openai_codex import Codex, CodexConfig, Sandbox
        except ImportError as exc:
            raise RuntimeError("Install openai-codex before generating signatures: pip install openai-codex") from exc
        with Codex(CodexConfig(cwd=str(REPOSITORY))) as codex:
            for report in reports:
                number = issue_number(report)
                try:
                    thread = codex.thread_start(model=args.model, sandbox=Sandbox.read_only, cwd=str(REPOSITORY))
                    signature = parse_response(thread.run(prompt_for(report), output_schema=OUTPUT_SCHEMA).final_response)
                    prefix = CORPORA[args.corpus]["signature_prefix"]
                    write_json(SIGNATURES / f"{prefix}_{number}.json", signature_record(number, signature, args.model))
                    print(f"#{number}: {signature['summary']}", flush=True)
                except Exception as exc:
                    print(f"FAILED #{number}: {exc}", file=sys.stderr, flush=True)
    elif not args.recluster_only:
        print("No reports require workflow generation.")
    signatures = load_signatures(args.corpus)
    state = cluster_signatures(signatures, args.embedding_model, args.similarity_threshold)
    write_json(CLUSTERS_PATH, state)
    print(f"{len(state['clusters'])} workflow clusters recorded in {CLUSTERS_PATH.relative_to(REPOSITORY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

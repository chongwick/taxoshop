#!/usr/bin/env python3
"""Synthesize evidence-backed macro-taxonomy entries from workflow clusters.

For every workflow cluster, Codex reads the *full* detailed reports for all
member issues—not just the workflow signatures—and identifies the most useful
general failure pattern they support. Results are checkpointed per cluster in
``taxos/macro_taxo`` and can safely be resumed after an interruption.

Requires Python 3.10+, ``pip install openai-codex``, and an authenticated local
Codex installation.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai_codex import Codex, CodexConfig, Sandbox


REPOSITORY = Path(__file__).resolve().parent
REPORTS = REPOSITORY / "taxos" / "micro_taxo"
WORKFLOWS = REPOSITORY / "taxos" / "workflow_signatures" / "clusters.json"
OUTPUT = REPOSITORY / "taxos" / "macro_taxo"
INDEX = OUTPUT / "index.json"
CLUSTER_ID = re.compile(r"workflow-\d{4}$")

OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "pattern",
        "description",
        "precondition",
        "critical_operation",
        "interference",
        "invalid_assumption",
        "failure",
        "search_strategy",
        "evidence",
        "scope_note",
    ],
    "properties": {
        "pattern": {"type": "string", "minLength": 12, "maxLength": 160},
        "description": {"type": "string", "minLength": 40, "maxLength": 700},
        "precondition": {"type": "string", "minLength": 12, "maxLength": 500},
        "critical_operation": {"type": "string", "minLength": 12, "maxLength": 500},
        "interference": {"type": "string", "minLength": 12, "maxLength": 500},
        "invalid_assumption": {"type": "string", "minLength": 12, "maxLength": 500},
        "failure": {"type": "string", "minLength": 12, "maxLength": 500},
        "search_strategy": {
            "type": "array",
            "minItems": 2,
            "maxItems": 6,
            "items": {"type": "string", "minLength": 12, "maxLength": 350},
        },
        "evidence": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["issue", "supports"],
                "properties": {
                    "issue": {"type": "integer"},
                    "supports": {"type": "string", "minLength": 12, "maxLength": 350},
                },
            },
        },
        "scope_note": {"type": "string", "minLength": 20, "maxLength": 500},
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gpt-5.6-luna", help="Codex model to use")
    parser.add_argument("--limit", type=int, help="process at most this many pending clusters")
    parser.add_argument("--only", nargs="+", metavar="CLUSTER", help="process only these workflow IDs")
    parser.add_argument("--force", action="store_true", help="regenerate entries that already exist")
    parser.add_argument("--dry-run", action="store_true", help="show the clusters that would be processed")
    return parser.parse_args()


def read_clusters() -> dict[str, dict[str, Any]]:
    data = json.loads(WORKFLOWS.read_text())
    clusters = data.get("clusters")
    if data.get("schema_version") != 1 or not isinstance(clusters, dict):
        raise ValueError(f"Unsupported workflow state in {WORKFLOWS}")
    return clusters


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def pending_clusters(args: argparse.Namespace, clusters: dict[str, dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    selected = set(args.only or clusters)
    unknown = selected - set(clusters)
    if unknown:
        raise ValueError(f"Unknown workflow cluster(s): {', '.join(sorted(unknown))}")
    entries = [(cluster_id, clusters[cluster_id]) for cluster_id in sorted(selected)]
    if not args.force:
        entries = [(cluster_id, cluster) for cluster_id, cluster in entries if not (OUTPUT / f"{cluster_id}.json").exists()]
    return entries[: args.limit] if args.limit else entries


def report_paths(issues: list[int]) -> list[str]:
    paths = []
    for issue in issues:
        path = REPORTS / f"gh_{issue}.md"
        if not path.exists():
            raise FileNotFoundError(f"Cluster report is missing: {path}")
        paths.append(str(path.relative_to(REPOSITORY)))
    return paths


def prompt_for(cluster_id: str, cluster: dict[str, Any]) -> str:
    issues = cluster["issues"]
    reports = "\n".join(f"- {path}" for path in report_paths(issues))
    workflow = "\n".join(f"{index}. {step}" for index, step in enumerate(cluster["workflow"], 1))
    return f"""You are creating one macro-taxonomy entry from a workflow cluster.

Cluster ID: {cluster_id}
Workflow hypothesis (a clue only; do not treat it as evidence):
{cluster['summary']}
{workflow}

Read every full detailed bug analysis below before answering. Do not edit files.
{reports}

Determine what actually generalizes across these reports. The reports are the
evidence; the workflow hypothesis may be incomplete or overly narrow. Produce a
useful, technically precise pattern, not a list of symptoms and not a restatement
of project-specific code. Remove CPython-specific names, APIs, types, test names,
file names, issue numbers, and implementation identifiers wherever a general term
can express the same mechanism.

The fields must form one causal chain: precondition → critical operation →
interference → invalid assumption → failure. Every mandatory claim must be
supported by the reports. If the cluster is a singleton, make a cautiously scoped
pattern and say so in scope_note. If reports differ in nonessential details,
describe the shared mechanism and use scope_note to state the boundary rather than
inventing a broader rule.

search_strategy must be 2–6 concrete code-review searches phrased as imperative
checks. evidence must include every issue in the cluster exactly once, and explain
what that report supports using generalized language.

Return only JSON matching the supplied schema."""


def validate_entry(data: Any, issues: list[int]) -> dict[str, Any]:
    if not isinstance(data, dict) or set(data) != set(OUTPUT_SCHEMA["required"]):
        raise ValueError("Codex response did not contain the expected macro-taxonomy fields")
    for field in ("pattern", "description", "precondition", "critical_operation", "interference", "invalid_assumption", "failure", "scope_note"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(f"Codex returned an empty {field}")
    if not isinstance(data["search_strategy"], list) or not 2 <= len(data["search_strategy"]) <= 6 or not all(isinstance(item, str) and item.strip() for item in data["search_strategy"]):
        raise ValueError("Codex returned an invalid search strategy")
    evidence = data["evidence"]
    if not isinstance(evidence, list) or {item.get("issue") for item in evidence if isinstance(item, dict)} != set(issues) or len(evidence) != len(issues):
        raise ValueError("Codex evidence must cover every cluster issue exactly once")
    if not all(isinstance(item.get("supports"), str) and item["supports"].strip() for item in evidence):
        raise ValueError("Codex returned invalid evidence")
    return data


def markdown(entry: dict[str, Any]) -> str:
    lines = [f"# {entry['pattern']}", "", entry["description"], ""]
    fields = [
        ("Precondition", entry["precondition"]),
        ("Critical operation", entry["critical_operation"]),
        ("Interference", entry["interference"]),
        ("Invalid assumption", entry["invalid_assumption"]),
        ("Failure", entry["failure"]),
        ("Scope", entry["scope_note"]),
    ]
    for title, value in fields:
        lines.extend([f"## {title}", "", value, ""])
    lines.extend(["## Search strategy", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(entry["search_strategy"], 1))
    lines.extend(["", "## Evidence", ""])
    for item in sorted(entry["evidence"], key=lambda value: value["issue"]):
        lines.append(f"- [#{item['issue']}](../micro_taxo/gh_{item['issue']}.md): {item['supports']}")
    return "\n".join(lines) + "\n"


def rebuild_index() -> None:
    records = []
    for path in sorted(OUTPUT.glob("workflow-*.json")):
        entry = json.loads(path.read_text())
        records.append({
            "cluster_id": entry["cluster_id"],
            "pattern": entry["pattern"],
            "issues": entry["issues"],
            "file": path.name,
        })
    write_json(INDEX, {"schema_version": 1, "entries": records})


def main() -> int:
    args = parse_args()
    clusters = read_clusters()
    selected = pending_clusters(args, clusters)
    if args.dry_run:
        print("Would process:", ", ".join(cluster_id for cluster_id, _ in selected) or "none")
        return 0
    if not selected:
        rebuild_index()
        print("No macro-taxonomy entries require generation.")
        return 0

    with Codex(CodexConfig(cwd=str(REPOSITORY))) as codex:
        for cluster_id, cluster in selected:
            issues = cluster["issues"]
            try:
                thread = codex.thread_start(model=args.model, sandbox=Sandbox.read_only, cwd=str(REPOSITORY))
                result = thread.run(prompt_for(cluster_id, cluster), output_schema=OUTPUT_SCHEMA)
                entry = validate_entry(json.loads(result.final_response), issues)
                record = {
                    "schema_version": 1,
                    "cluster_id": cluster_id,
                    "issues": issues,
                    "workflow_hypothesis": cluster["summary"],
                    "pattern": entry["pattern"],
                    "description": entry["description"],
                    "precondition": entry["precondition"],
                    "critical_operation": entry["critical_operation"],
                    "interference": entry["interference"],
                    "invalid_assumption": entry["invalid_assumption"],
                    "failure": entry["failure"],
                    "search_strategy": entry["search_strategy"],
                    "evidence": entry["evidence"],
                    "scope_note": entry["scope_note"],
                    "model": args.model,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }
                write_json(OUTPUT / f"{cluster_id}.json", record)
                (OUTPUT / f"{cluster_id}.md").write_text(markdown(record))
                rebuild_index()
                print(f"{cluster_id} → {record['pattern']}", flush=True)
            except Exception as exc:
                print(f"FAILED {cluster_id}: {exc}", file=sys.stderr, flush=True)
    rebuild_index()
    print(f"Macro taxonomy index: {INDEX.relative_to(REPOSITORY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

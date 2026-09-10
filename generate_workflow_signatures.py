#!/usr/bin/env python3
"""Generate abstract bug workflows and cluster equivalent workflows with Codex.

The script reads each detailed Markdown report under ``taxos/micro_taxo`` in a
read-only Codex thread.  Codex returns a compact, product-agnostic workflow and
either selects an existing workflow cluster or requests a new one.  Progress is
persisted after every report, so an interrupted run is safe to resume.

Requires Python 3.10+ and ``pip install openai-codex``.  Codex must already be
authenticated on the machine that runs this script.
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
SIGNATURES = REPORTS / "workflow_signatures"
CLUSTERS_PATH = REPORTS / "workflow_clusters.json"
REPORT_NUMBER = re.compile(r"gh_(\d+)\.md$")

OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["workflow", "summary", "selected_cluster_id", "decision_reason"],
    "properties": {
        "workflow": {
            "type": "array",
            "minItems": 2,
            "maxItems": 8,
            "items": {"type": "string", "minLength": 8, "maxLength": 180},
            "description": "Ordered, general workflow steps.",
        },
        "summary": {
            "type": "string",
            "minLength": 16,
            "maxLength": 300,
            "description": "A concise, implementation-neutral workflow label.",
        },
        "selected_cluster_id": {
            "type": ["string", "null"],
            "description": "An exact existing ID, or null for a new workflow cluster.",
        },
        "decision_reason": {
            "type": "string",
            "minLength": 8,
            "maxLength": 300,
            "description": "Why this workflow belongs in the selected cluster or is distinct.",
        },
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gpt-5.6-terra", help="Codex model to use")
    parser.add_argument("--limit", type=int, help="process at most this many unprocessed reports")
    parser.add_argument("--only", nargs="+", type=int, metavar="ISSUE", help="process only these issue numbers")
    parser.add_argument("--force", action="store_true", help="regenerate signatures that already exist")
    parser.add_argument("--dry-run", action="store_true", help="show which reports would be processed")
    return parser.parse_args()


def load_clusters() -> dict[str, Any]:
    if not CLUSTERS_PATH.exists():
        return {"schema_version": 1, "clusters": {}}
    state = json.loads(CLUSTERS_PATH.read_text())
    if state.get("schema_version") != 1 or not isinstance(state.get("clusters"), dict):
        raise ValueError(f"Unsupported cluster state in {CLUSTERS_PATH}")
    return state


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
    reports = sorted(REPORTS.glob("gh_*.md"), key=issue_number)
    if args.only:
        requested = set(args.only)
        reports = [path for path in reports if issue_number(path) in requested]
        found = {issue_number(path) for path in reports}
        missing = requested - found
        if missing:
            raise ValueError(f"No rendered report for issue(s): {', '.join(map(str, sorted(missing)))}")
    if not args.force:
        reports = [path for path in reports if not (SIGNATURES / f"gh_{issue_number(path)}.json").exists()]
    return reports[: args.limit] if args.limit else reports


def cluster_catalog(state: dict[str, Any]) -> str:
    clusters = state["clusters"]
    if not clusters:
        return "No clusters exist yet. Set selected_cluster_id to null."
    entries = []
    for cluster_id, cluster in sorted(clusters.items()):
        steps = " → ".join(cluster["workflow"])
        entries.append(f"- {cluster_id}: {cluster['summary']} | {steps} | members: {len(cluster['issues'])}")
    return "\n".join(entries)


def prompt_for(report: Path, state: dict[str, Any]) -> str:
    relative_report = report.relative_to(REPOSITORY)
    return f"""Read the detailed bug analysis at `{relative_report}`. Do not edit any files.

Create a workflow signature that makes this bug comparable to bugs from unrelated
projects. Describe the causal sequence, not source-code identifiers. Deliberately
remove CPython-specific names, API names, test names, file names, issue IDs,
library names, platform release names, and project-specific terminology whenever
an accurate general term exists. Preserve the bug mechanism and ordering.

For example, prefer 'a worker exits while shared state is being torn down' over
names of a runtime, class, test, or function. Do not merely restate the title.

Choose an existing cluster only when its underlying failure workflow is materially
the same, even if its symptoms, files, or implementation details differ. Otherwise
set selected_cluster_id to null. selected_cluster_id must exactly match one of the
existing IDs below. A workflow must have 2–8 concise ordered steps.

Existing workflow clusters:
{cluster_catalog(state)}

Return only JSON matching the supplied schema."""


def parse_response(text: str, known_clusters: set[str]) -> dict[str, Any]:
    """Accept SDK structured output and tolerate an accidental Markdown fence."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S).strip()
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Codex response was not a JSON object")
    if set(data) != set(OUTPUT_SCHEMA["required"]):
        raise ValueError("Codex response did not contain the expected fields")
    workflow = data["workflow"]
    if not isinstance(workflow, list) or not 2 <= len(workflow) <= 8 or not all(isinstance(step, str) and step.strip() for step in workflow):
        raise ValueError("Codex response contains an invalid workflow")
    selected = data["selected_cluster_id"]
    if selected is not None and selected not in known_clusters:
        raise ValueError(f"Codex selected unknown cluster {selected!r}")
    if not all(isinstance(data[field], str) and data[field].strip() for field in ("summary", "decision_reason")):
        raise ValueError("Codex response contains an empty textual field")
    return {key: [step.strip() for step in workflow] if key == "workflow" else value.strip() if isinstance(value, str) else value for key, value in data.items()}


def next_cluster_id(state: dict[str, Any]) -> str:
    numbers = [int(match.group(1)) for key in state["clusters"] if (match := re.fullmatch(r"workflow-(\d+)", key))]
    return f"workflow-{max(numbers, default=0) + 1:04d}"


def remove_from_existing_cluster(state: dict[str, Any], number: int) -> None:
    for cluster_id, cluster in list(state["clusters"].items()):
        if number in cluster["issues"]:
            cluster["issues"].remove(number)
            if not cluster["issues"]:
                del state["clusters"][cluster_id]


def record_signature(state: dict[str, Any], number: int, signature: dict[str, Any], model: str) -> dict[str, Any]:
    remove_from_existing_cluster(state, number)
    cluster_id = signature["selected_cluster_id"] or next_cluster_id(state)
    cluster = state["clusters"].get(cluster_id)
    if cluster is None:
        cluster = {"summary": signature["summary"], "workflow": signature["workflow"], "issues": []}
        state["clusters"][cluster_id] = cluster
    cluster["issues"].append(number)
    cluster["issues"].sort()
    return {
        "schema_version": 1,
        "issue": number,
        "cluster_id": cluster_id,
        "workflow": signature["workflow"],
        "summary": signature["summary"],
        "decision_reason": signature["decision_reason"],
        "model": model,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    args = parse_args()
    state = load_clusters()
    reports = reports_to_process(args)
    if args.dry_run:
        print("Would process:", ", ".join(str(issue_number(path)) for path in reports) or "none")
        return 0
    if not reports:
        print("No reports require workflow signatures.")
        return 0

    with Codex(CodexConfig(cwd=str(REPOSITORY))) as codex:
        for report in reports:
            number = issue_number(report)
            try:
                thread = codex.thread_start(model=args.model, sandbox=Sandbox.read_only, cwd=str(REPOSITORY))
                result = thread.run(prompt_for(report, state), output_schema=OUTPUT_SCHEMA)
                signature = parse_response(result.final_response, set(state["clusters"]))
                record = record_signature(state, number, signature, args.model)
                write_json(SIGNATURES / f"gh_{number}.json", record)
                write_json(CLUSTERS_PATH, state)
                print(f"#{number} → {record['cluster_id']}: {record['summary']}", flush=True)
            except Exception as exc:
                print(f"FAILED #{number}: {exc}", file=sys.stderr, flush=True)
    print(f"{len(state['clusters'])} workflow clusters recorded in {CLUSTERS_PATH.relative_to(REPOSITORY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

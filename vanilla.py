#!/usr/bin/env python3
"""
Run a long-term repository audit with the Claude Agent SDK until a $20 budget
is used up. If Claude stops early, the session is resumed with a
"keep going" prompt and whatever budget remains.

Usage:
    pip install -U claude-agent-sdk
    export ANTHROPIC_API_KEY=...
    python audit.py /path/to/repo [--budget 20] [--model <model>] [--timeout-hours 8]
"""
import argparse
import json
import shutil
import signal
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

PROMPT = (
    "Audit CPython. Use the included Dockerfile to confirm findings with "
    "the sanitizer-enabled build. This is a long-term audit. Do not stop after "
    "first discovery."
)

CONTINUE_PROMPT = (
    "Continue the audit. About ${remaining:.2f} of budget remains. Review "
    "NOTES.md.")#, then look for new issues in code, components, or bug "
    #"classes you have not examined yet, and confirm each with the "
    #"sanitizer-enabled build. Do not re-report existing findings."

APPEND = (
    "Record each finding in an \"audit_#\" directory. In this directory, keep a \"findings\" subdirectory where you will record all new findings. Keep a NOTES.md. In a \"logs\" subdirectory, store full sanitizer outputs of PoCs. In a \"repro\" subdirectory, keep reproducers. "
    "Whenever you run Docker containers, pass `--label taxoshop-audit=1` on the "
    "`docker run` command so the harness can clean them up if the run is interrupted."
)

# Containers the agent is told to label; used for best-effort cleanup on exit.
DOCKER_LABEL = "taxoshop-audit=1"

MIN_REMAINING_USD = 0.50  # don't start a round with less than this left
MAX_ROUNDS = 50           # hard cap on resume rounds
STALL_COST_USD = 0.10     # a round cheaper than this counts as a stall...
STALL_LIMIT = 2           # ...and this many stalls in a row ends the audit


def cleanup_docker():
    """Best-effort removal of containers the agent labelled for this run.

    Only touches containers carrying DOCKER_LABEL, so it can never kill
    unrelated containers. Silent no-op if docker isn't installed.
    """
    if not shutil.which("docker"):
        return
    try:
        ids = subprocess.run(
            ["docker", "ps", "-aq", "--filter", f"label={DOCKER_LABEL}"],
            capture_output=True, text=True, timeout=15,
        ).stdout.split()
        if ids:
            print(f"[cleaning up {len(ids)} labelled container(s)]", flush=True)
            subprocess.run(["docker", "rm", "-f", *ids],
                           capture_output=True, timeout=60)
    except Exception as e:  # cleanup is best-effort; never mask the real exit
        print(f"[docker cleanup skipped: {e}]", flush=True)


def make_options(repo, model, budget, resume):
    return ClaudeAgentOptions(
        cwd=str(repo),
        system_prompt={"type": "preset", "preset": "claude_code", "append": APPEND},
        setting_sources=["user", "project", "local"],
        # Unattended run: no permission prompts (needed for docker build/run).
        # Run this on a disposable VM or machine you're comfortable handing over.
        permission_mode="bypassPermissions",
        # No web access through Claude's built-in tools
        disallowed_tools=["WebSearch", "WebFetch"],
        max_budget_usd=budget,  # counts only this round's own spend
        model=model,
        resume=resume,
    )


async def run_round(prompt, options, log):
    result = None
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(block.text, flush=True)
                    log.write(json.dumps({"text": block.text}) + "\n")
                elif isinstance(block, ToolUseBlock):
                    print(f"  -> {block.name}: {json.dumps(block.input)[:200]}", flush=True)
                    log.write(json.dumps({"tool": block.name, "input": block.input}) + "\n")
            log.flush()
        elif isinstance(msg, ResultMessage):
            result = msg
    return result


async def audit(*, repo, budget, model, log, state):
    prompt, stalls = PROMPT, 0
    while len(state["rounds"]) < MAX_ROUNDS:
        remaining = budget - state["spent"]
        if remaining < MIN_REMAINING_USD:
            state["stop_reason"] = "budget_exhausted"
            return

        n = len(state["rounds"]) + 1
        print(f"\n===== Round {n} (${remaining:.2f} remaining) =====\n", flush=True)
        options = make_options(repo, model, remaining, state["session_id"])
        result = await run_round(prompt, options, log)
        if result is None:
            state["stop_reason"] = "no_result"
            return

        state["session_id"] = result.session_id
        reported = result.total_cost_usd or 0.0
        # Resumed rounds report the session's cumulative cost. Older SDK
        # versions reported per-call cost; the fallback handles that.
        round_cost = reported - state["spent"]
        if round_cost < 0:
            round_cost = reported
        state["spent"] += round_cost

        record = {
            "round": n,
            "subtype": result.subtype,
            "round_cost_usd": round(round_cost, 4),
            "spent_usd": round(state["spent"], 4),
            "num_turns": result.num_turns,
            "duration_api_ms": result.duration_api_ms,
        }
        state["rounds"].append(record)
        log.write(json.dumps(record) + "\n")
        log.flush()

        if result.subtype != "success":  # e.g. error_max_budget_usd
            state["stop_reason"] = result.subtype
            return
        stalls = stalls + 1 if round_cost < STALL_COST_USD else 0
        if stalls >= STALL_LIMIT:
            state["stop_reason"] = "stalled"
            return
        prompt = CONTINUE_PROMPT.format(remaining=budget - state["spent"])

    state["stop_reason"] = "max_rounds"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("repo", type=Path)
    p.add_argument("--budget", type=float, default=10.0)
    p.add_argument("--model", default="claude-opus-4-8", help="defaults to 4.8")
    p.add_argument("--timeout-hours", type=float, default=8.0,
                   help="wall-clock safety net in case the run hangs")
    args = p.parse_args()

    repo = args.repo.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = Path(f"audit-{repo.name}-{stamp}.jsonl")
    state = {"spent": 0.0, "rounds": [], "session_id": None, "stop_reason": None}

    async def guarded():
        with log_path.open("w") as log:
            async with anyio.create_task_group() as tg:
                # First SIGINT (Ctrl-C) or SIGTERM cancels the audit cleanly
                # instead of tearing the process down with KeyboardInterrupt.
                async def watch_signals():
                    with anyio.open_signal_receiver(
                            signal.SIGINT, signal.SIGTERM) as signals:
                        async for _ in signals:
                            state["stop_reason"] = "interrupted"
                            print("\n[interrupt received — shutting down "
                                  "cleanly; press Ctrl-C again to force quit]",
                                  flush=True)
                            tg.cancel_scope.cancel()
                            return

                tg.start_soon(watch_signals)
                with anyio.move_on_after(args.timeout_hours * 3600) as scope:
                    await audit(repo=repo, budget=args.budget, model=args.model,
                                log=log, state=state)
                if scope.cancelled_caught:
                    state["stop_reason"] = "timeout"
                    print(f"\n[timed out after {args.timeout_hours}h]")
                # Audit finished on its own -> stop the signal watcher so the
                # task group can exit.
                tg.cancel_scope.cancel()

    started_at = datetime.now()
    t0 = time.monotonic()
    try:
        anyio.run(guarded)
    except KeyboardInterrupt:
        # A second Ctrl-C during graceful shutdown (or one arriving outside the
        # signal-receiver window) lands here. Still fall through to write the
        # summary rather than dying with a traceback.
        if state["stop_reason"] is None:
            state["stop_reason"] = "interrupted"
    finally:
        cleanup_docker()
    wall_seconds = time.monotonic() - t0
    ended_at = datetime.now()

    summary = {
        "summary": True,
        "repo": str(repo),
        "started_at": started_at.isoformat(timespec="seconds"),
        "ended_at": ended_at.isoformat(timespec="seconds"),
        "wall_clock_seconds": round(wall_seconds, 1),
        "stop_reason": state["stop_reason"],
        "cost_usd": round(state["spent"], 4),
        "budget_usd": args.budget,
        "rounds": len(state["rounds"]),
        "session_id": state["session_id"],
    }
    with log_path.open("a") as log:
        log.write(json.dumps(summary) + "\n")

    print("\n" + "=" * 60)
    print(f"Started     : {summary['started_at']}")
    print(f"Ended       : {summary['ended_at']}")
    print(f"Wall clock  : {timedelta(seconds=round(wall_seconds))}")
    print(f"Stop reason : {summary['stop_reason']}")
    print(f"Cost        : ${state['spent']:.2f} of ${args.budget:.2f}")
    print(f"Rounds      : {summary['rounds']}")
    print(f"Session ID  : {state['session_id']}  (resume with `claude --resume <id>`)")
    print(f"Findings    : {repo / 'AUDIT_FINDINGS.md'}")
    print(f"Full log    : {log_path}")


if __name__ == "__main__":
    main()

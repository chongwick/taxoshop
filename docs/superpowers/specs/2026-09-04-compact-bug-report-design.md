# Compact Bug Report Micro-Taxos

## Goal

Replace the source-record micro-taxo with a compact, evidence-backed bug
analysis report. Each report captures the bug report, linked patch material,
code review feedback, proof-of-concept or reproducer code, and full sanitizer
or crash output when present.

## Evidence Collection

For every GitHub issue, fetch its issue record and comments. Identify explicit
GitHub pull-request and commit links in that discussion. For each linked pull
request, fetch the pull request record, its full unified diff, review comments,
and review summaries. Commit links are retained as references and their patch
material is fetched when GitHub exposes it.

Extract fenced source-code blocks from the issue body, issue comments, linked
PR description, and review comments as candidate PoCs or reproducers. Extract
complete sanitizer, assertion, traceback, and crash-output blocks verbatim;
never summarize or truncate a detected sanitizer output block.

## Report Format

Each `workdir_python/micro_taxos/gh_<number>.md` report contains only:

1. `Bug Report`: a concise Codex synthesis of the issue report and relevant
   discussion, grounded in collected evidence.
2. `Patch(es)`: each linked PR or commit, its semantic change, and focused diff
   excerpts relevant to the bug.
3. `Code Review`: substantive review comments and author responses that affect
   correctness, scope, or the patch outcome.
4. `PoC / Reproducer`: relevant source blocks from issue or PR evidence,
   retained verbatim with a source link.
5. `Full Sanitizer / Crash Output`: complete matching output blocks retained
   verbatim with a source link; state `Not provided in fetched evidence` only
   when none is found.
6. `References`: issue, patch, commit, and review URLs used by the report.

The report excludes raw API JSON, generic metadata, irrelevant discussion, and
unsupported claims. Codex must mark unavailable evidence instead of inventing
details.

## Processing Sequence

For each issue, collect issue and patch evidence, generate and validate the
compact micro-taxo, write it atomically, generate the matching fingerprint from
the completed report, write the fingerprint atomically, and then process the
next issue. If collection or report generation fails, continue with the next
issue and record the failure. If fingerprint generation fails, retain the
completed report and record the failure.

## Verification

Tests use fake GitHub responses and a fake report generator to prove that
linked PR diffs and review comments reach the report prompt; only relevant
evidence appears in the report; a sanitizer block is verbatim and untruncated;
and fingerprint generation follows report writing.

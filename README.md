# taxoshop — CPython sanitizer pattern audit

A workbench for finding memory-safety and undefined-behavior bugs in CPython by matching
its code against a **taxonomy of recurring defect patterns**, then confirming each
candidate on an AddressSanitizer/UndefinedBehaviorSanitizer build of the interpreter.

The idea: past CPython bugs cluster into a small number of *families* (e.g. "reentrant
user code invalidates native state before later use"). Each family has a write-up with a
concrete **search strategy**. We use those to look for *new* instances, reproduce them
under sanitizers, and report the ones that are new and confirmed.

> **New here?** Read [`STARTUP.md`](STARTUP.md) — it has the full repo tour, the sanitizer
> build, run commands, and an ordered startup checklist.

## What's in this repo

| Path | What it is |
|------|------------|
| [`taxos/macro_taxo/`](taxos/macro_taxo) | The **pattern write-ups** (`workflow-XXXX.md`). Each: precondition, critical operation, interference, invalid assumption, failure, scope, **search strategy**, evidence. Start here. |
| [`taxos/workflow_signatures/`](taxos/workflow_signatures) | Clustering data. `clusters.json` maps each family → summary + known issue numbers; `gh_*.json` is one signature per known GitHub issue. |
| [`taxos/micro_taxo/`](taxos/micro_taxo) | Per-issue write-ups (`gh_NNNNN.md`) and source material. |
| [`tally_bugs.py`](tally_bugs.py) | Ranks the pattern families by how many known issues cluster to them. |
| `generate_*.py` | Generators that produced the taxonomy (`generate_macro_taxonomy.py`, `generate_reports.py`, `generate_workflow_signatures.py`). |
| [`Dockerfile`](Dockerfile) | Multi-stage build of CPython (`origin/main`) with ASan+UBSan (`asan-ubsan`, the default target) and ThreadSanitizer (`tsan`). |
| `cpython/` | Full CPython checkout — read the interpreter source here. |
| `audit<N>/` | One workspace per audit iteration: `NOTES.md`, `findings/`, `logs/`, `repro/`. |

## Quick start

```bash
# 1. See which pattern families are highest-yield
python3 tally_bugs.py

# 2. Read the top families you'll target
$EDITOR taxos/macro_taxo/workflow-0137.md   # reentrant conversion invalidates a resource
$EDITOR taxos/macro_taxo/workflow-0080.md   # callback re-entrancy
$EDITOR taxos/macro_taxo/workflow-0014.md   # retained pointer used after owner releases

# 3. Reuse the sanitizer image if it exists (the build is slow); otherwise build it
docker images | grep -iE "cpython|asan"
# build only if missing:
docker build --target asan-ubsan -t taxoshop/cpython-asan-ubsan:current .

# 4. Verify what the image contains
docker run --rm taxoshop/cpython-asan-ubsan:current \
  bash -c './python -V; cd /src/cpython && git rev-parse HEAD'

# 5. Run a reproducer under sanitizers (own dir mounted at /audit)
docker run --rm -v "$PWD/audit4:/audit" taxoshop/cpython-asan-ubsan:current \
  bash -c 'cd /src/cpython && ./python /audit/repro/textio_detach_uaf.py'
```

A clean run prints your final output; a confirmed bug prints an `AddressSanitizer:` /
`UndefinedBehaviorSanitizer:` block and aborts.

## The sanitizer build (essentials)

- Default target **`asan-ubsan`**: `--with-address-sanitizer
  --with-undefined-behavior-sanitizer --without-pymalloc`, `PYTHONMALLOC=malloc`.
  Interpreter at `/src/cpython/python`.
- Because `PYTHONMALLOC=malloc`, heap allocations go through `malloc`, so ASan **catches
  heap UAF/OOB** in normal Python objects. ASan does **not** poison `mmap()` pages — mmap
  OOB only faults when it hits an unmapped page (e.g. after `resize()`).

## Working rules

- **No `ctypes`** in reproducers — bugs must be reachable through ordinary Python.
- Only report issues that are **new and sanitizer-confirmed**. Check open/closed CPython
  issues (`gh issue list`/`gh search issues`) and `git log --grep` first.
- This is a **long-running** effort: keep running notes in `audit<N>/NOTES.md` (including
  the map of modules already verified hardened, so they aren't re-audited).
- We **audit and report only** — we do not modify CPython source from here
  (see `cpython/.claude/CLAUDE.md` for CPython's AI-tools policy).

## Findings

Each confirmed bug is written up in `audit<N>/findings/FINDING-00X-<slug>.md` with its
parent pattern (`workflow-XXXX`), root cause (`file:line`), a minimal reproducer, the full
sanitizer output, scope, and a duplicate analysis. Latest:

- `audit4/findings/FINDING-001-textio-detach-uaf.md` — heap use-after-free in
  `io.TextIOWrapper`'s read path via a reentrant `detach()` (pattern `workflow-0137`).

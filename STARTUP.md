# STARTUP — CPython Sanitizer Pattern Audit

Read this first. It lets a new audit skip repository discovery and get straight to
hunting. It captures the repo layout, the taxonomy data model, the sanitizer build, and
the exact commands used to bring up and confirm findings.

**Mission:** find CPython bugs that match the recurring patterns in `taxos/macro_taxo`,
confirm each on the ASan/UBSan build, avoid duplicates (upstream *and* prior audits),
and write them up with full sanitizer output.

**Hard constraints:**
- **Do NOT use `ctypes`** in any reproducer.
- Only report **new + sanitizer-confirmed** issues. Check open/closed CPython issues first.
- This is a **long-running** audit — keep running notes; don't stop at the first dead end.

---

## 1. Repository layout

```
taxoshop/
├── Dockerfile                       # multi-stage: builds CPython with sanitizers
├── .dockerignore
├── cpython/                         # full CPython checkout (origin/main), read the source here
├── taxos/
│   ├── bugs.txt                     # raw bug list
│   ├── macro_taxo/                  # *** THE PATTERN WRITE-UPS ***  (read these)
│   │   ├── index.json               # {schema_version, entries}
│   │   └── workflow-XXXX.md/.json   # one file per pattern family (~164)
│   ├── micro_taxo/                  # per-issue write-ups gh_NNNNN.md + sources/
│   └── workflow_signatures/         # *** CLUSTERING DATA ***
│       ├── clusters.json            # {clusters: {workflow-XXXX: {summary, workflow[], issues[]}}}
│       └── gh_NNNNNN.json           # one per known GitHub issue, has cluster_id + issue
├── tally_bugs.py                    # ranks pattern families by how many known issues cluster to them
├── generate_macro_taxonomy.py       # (generator — how macro_taxo was produced)
├── generate_reports.py
├── generate_workflow_signatures.py
├── dedups.txt
└── audit4/                          # current audit workspace (see §5); audit2/audit3 were prior, now deleted
```

### The taxonomy data model (how the pieces connect)
- **`taxos/macro_taxo/workflow-XXXX.md`** — a human-readable *pattern* (defect family):
  Precondition / Critical operation / Interference / Invalid assumption / Failure /
  Scope / **Search strategy** / **Evidence** (`#NNNNN` links to known issues). These are
  your hunting guides — the "Search strategy" section literally tells you where to look.
- **`taxos/workflow_signatures/clusters.json`** — maps each `workflow-XXXX` cluster id to
  a `summary`, a step-by-step `workflow`, and the list of `issues` (GitHub numbers) that
  belong to it.
- **`taxos/workflow_signatures/gh_NNNNNN.json`** — one signature per known issue, carrying
  its `cluster_id`. `tally_bugs.py` counts these to rank families.

### Run the clustering to see the highest-yield families
```bash
cd taxoshop && python3 tally_bugs.py
```
Top families are all reentrancy / use-after-invalidation (counts as of last run):
- `workflow-0014` (38) — retained pointer dereferences storage after its owner releases it.
- `workflow-0080` (22) — callback re-entrancy invalidates borrowed state/backing storage.
- `workflow-0137` (20) — reentrant argument conversion invalidates a backing resource.
- then `workflow-0077/0091/0081/...` (concurrency, error-path leaks, zero-len memcpy, etc.)

Read at least `workflow-0137.md`, `workflow-0080.md`, `workflow-0014.md` before hunting.
Other confirmable, less-swept families: `0005` (zero-length memcpy w/ NULL — UBSan),
`0003` (signed left-shift UB — UBSan), `0007` (misaligned typed access), `0010`
(float→int OOB before validation).

---

## 2. The sanitizer build (Dockerfile)

`Dockerfile` has stages:
- `build-base` — Ubuntu 24.04, clones CPython `origin/main` (`ARG CPYTHON_REF=origin/main`,
  depth 5000) into `/src/cpython`.
- **`asan-ubsan`** (default target) — `./configure --with-address-sanitizer
  --with-undefined-behavior-sanitizer --without-pymalloc --without-ensurepip`; `make`.
  Interpreter at `/src/cpython/python`. Env baked in:
  `ASAN_OPTIONS=detect_leaks=0:abort_on_error=1:symbolize=1`,
  `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`, `PYTHONMALLOC=malloc`.
- `tsan` — ThreadSanitizer variant (for concurrency/free-threading families).

### Do NOT rebuild if an image already exists
Check first:
```bash
docker images | grep -iE "cpython|asan|taxo"
```
Reuse **`taxoshop/cpython-asan-ubsan:current`** if present (build takes a long time; the
image auto-fetches current `origin/main`). Verify what it contains:
```bash
docker run --rm taxoshop/cpython-asan-ubsan:current \
  bash -c './python -c "import sys;print(sys.version)"; cd /src/cpython && git rev-parse HEAD'
```
Last confirmed: `3.16.0a0`, HEAD `e5d4fa281c573b764b827f3defae260787024e43`.

To (re)build the default ASan/UBSan target only if needed:
```bash
cd /Users/danielchong/Repositories/taxoshop
docker build --target asan-ubsan -t taxoshop/cpython-asan-ubsan:current . 2>&1 | tee audit<N>/logs/docker-build.log
```

### Critical toolchain fact
ASan instruments heap allocations (PyMem/PyObject → `malloc` because `PYTHONMALLOC=malloc`),
so **heap UAF/OOB in list/dict/bytes/bytearray/array/unicode/most objects IS caught**.
ASan does **NOT** poison `mmap()` pages — mmap OOB only crashes if it hits an *unmapped*
page (SEGV), e.g. after `resize()` shrinks/moves the mapping. Design repros accordingly.

---

## 3. Running reproducers

Mount an audit dir into the container and run each repro in its own process (ASan aborts
the whole process on the first error):
```bash
docker run --rm -v /Users/danielchong/Repositories/taxoshop/audit<N>:/audit \
  taxoshop/cpython-asan-ubsan:current \
  bash -c 'cd /src/cpython && ./python /audit/repro/<file>.py'
```
Batch loop (isolated per file):
```bash
docker run --rm -v /Users/danielchong/Repositories/taxoshop/audit<N>:/audit \
  taxoshop/cpython-asan-ubsan:current bash -c '
  cd /src/cpython
  for f in /audit/repro/battery/t_*.py; do
    echo "===== $f ====="; ./python "$f" 2>&1 | tail -6; echo "[exit ${PIPESTATUS[0]}]"
  done'
```
A clean run prints your final `print(...)`; a confirmed bug prints an
`AddressSanitizer:`/`UndefinedBehaviorSanitizer:` block and aborts (exit 134/SEGV).
Save the full block to `audit<N>/logs/<name>.asan.txt`.

---

## 4. Duplicate checking (required before write-up)

Prior local audits and a large **upstream sweep** already fixed most obvious cases
(gh-142xxx..154xxx across mmap, array, bytearray, memoryview, json, io, sqlite, struct,
socket, itertools, elementtree, pickle, ...). Always check both:
```bash
# upstream issues (needs gh auth; run from inside the cpython checkout)
cd cpython
gh issue list --repo python/cpython --search "<keywords>" --state all --limit 20
gh search issues --repo python/cpython "<symbol e.g. buffer_access_safe>" --limit 10
gh issue view <NNN> --repo python/cpython

# is a given fix already in the checkout?
git log --oneline -5000 --grep "gh-<NNN>"
git log --oneline -5000 | grep -iE "use-after-free|reentran|mutated during|concurrently mutat"
```
Known DUPES already reported upstream (do not re-file): `#157335` (mmap `__setitem__`
reentrant resize), `#154997` (BufferedIO `self->raw` NULL-deref via own detach),
`#154523` (free-threading data race on `self->buffer=NULL`).

Note: `cpython/.claude/CLAUDE.md` states CPython's AI-tools policy. We only *audit and
report* — we do not modify CPython source or open PRs from here.

---

## 5. Audit workspace convention

Each audit iteration gets its own top-level dir (`audit2`, `audit3`, `audit4`, ...):
```
audit<N>/
├── NOTES.md      # running log: method, candidate log (IDEA/TESTING/CONFIRMED/DUP/FALSE), hardened-module map
├── findings/     # FINDING-00X-<slug>.md  (parent pattern, root cause, repro, full ASan output, dup analysis)
├── logs/         # saved *.asan.txt sanitizer output + docker-build.log
└── repro/        # minimal reproducers; repro/battery/ = bulk scoping tests
```
**Read the latest `audit<N>/NOTES.md` before starting** — it has the map of modules
already verified hardened (so you don't re-audit them) and the confirmed/dup findings.

Persistent cross-session state is also in the auto-memory
(`.../memory/cpython-sanitizer-audit.md`, indexed in `MEMORY.md`).

---

## 6. Startup checklist (do these in order)

1. `python3 tally_bugs.py` → note top families.
2. Read `taxos/macro_taxo/workflow-0137.md`, `-0080.md`, `-0014.md` (+ any family you target).
3. `docker images | grep -iE "cpython|asan"` → reuse `taxoshop/cpython-asan-ubsan:current`;
   verify its HEAD (`git rev-parse HEAD`). Rebuild only if missing.
4. Create `audit<N>/{findings,logs,repro/battery}` and start `audit<N>/NOTES.md`.
5. Read prior `audit*/NOTES.md` + memory to skip already-hardened modules and known dupes.
6. Hunt: grep `cpython/Modules` & `cpython/Objects` for the family's idioms
   (`PyNumber_AsSsize_t`, `_PyNumber_Index`, `PyObject_GetBuffer`, `PyObject_RichCompareBool`,
   borrowed `self->x` used across a user-code call, size cached before a conversion, etc.);
   or fuzz empirically with "evil" objects (`__index__`/`__buffer__`/`__eq__`/`__hash__`/
   `readinto`/`fileno` that resize/clear/close/detach the target mid-operation).
7. Confirm on the ASan/UBSan image; save the log.
8. Dup-check (upstream `gh` + `git log`).
9. Write `findings/FINDING-00X-*.md`: parent `workflow-XXXX`, root cause with `file:line`,
   minimal repro, full sanitizer output, scope, and duplicate analysis.

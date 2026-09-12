# CPython Sanitizer Pattern Audit

Date: 2026-09-11

Scope: current CPython `origin/main` as fetched by the repository Dockerfile, ASan/UBSan build target.

## Setup

- Repository Dockerfile target: `asan-ubsan`
- Image tag: `taxoshop/cpython-asan-ubsan:current`
- Full no-cache build log: `logs/docker-build.log`

## Pattern Reading

Read `tally_bugs.py` and the macro taxonomy index. The clustering script counts workflow signature JSON files by `cluster_id` and prints the top recurring families. The highest-yield families for this audit are:

- `workflow-0014`: borrowed or derived handles survive reentrancy, mutation, concurrency, or teardown and are used after invalidation.
- `workflow-0080`: callback reentrancy invalidates borrowed state or backing storage during a native operation.
- `workflow-0137`: reentrant user-code execution invalidates native state before later use.
- `workflow-0077`: concurrent contexts access shared process-wide state without complete synchronization.
- `workflow-0091`: native error paths lose ownership of temporary state.
- `workflow-0081`: unsynchronized concurrent access to shared mutable storage/state.
- `workflow-0005`: zero-count memory transfers through absent or invalid storage.
- `workflow-0007`: raw storage or arbitrary addresses are used for stricter-aligned typed access.
- `workflow-0003`: signed left shift UB while constructing packed or bit-oriented values.

Working rule: candidates must be source-grounded, reachable through documented/public behavior, confirmed by the sanitizer build, and checked against open CPython issues before write-up.

## Running Log

- Created fresh audit directory `audit3/` with `logs/`, `notes/`, `repro/`, and `findings/`.
- Started a no-cache Docker build so the image fetches current `origin/main` instead of reusing a cached CPython checkout.

### 2026-09-11 — continuation

- **Build in use:** image `taxoshop/cpython-asan-ubsan:current`. Confirmed live: CPython
  `main` @ `e5d4fa281c573b764b827f3defae260787024e43` (3.16.0a0), gcc, ASan+UBSan,
  `--without-pymalloc`, `PYTHONMALLOC=malloc`. Toolchain validated end-to-end by
  reproducing crashes with symbolized source lines.

- **Candidate 1 — HZ incremental decoder OOB read (`_codecs_cn.c:417`).** Parent pattern
  `workflow-0036` (boundary-sensitive lookahead without proving the next element is
  in-buffer; evidence #101180, #127971). Root cause: `DECODER(hz)` reads
  `INBYTE2 == (*inbuf)[1]` on line 417 *before* the `REQUIRE_INBUF(2)` guard on line 419.
  Reproduced live (see `logs/hz_min_asan.txt` and re-run): 1-byte over-read of the
  `malloc(1)` pending buffer allocated at `multibytecodec.c:1201`.
  - Static cross-check across `_codecs_{cn,hk,kr,jp,tw,iso2022}.c`: every other decoder
    calls `REQUIRE_INBUF(n)` *before* any `INBYTEn`; the iso2022 escape parser proves the
    whole sequence in-bounds (loop returns `MBERR_TOOFEW` before computing `esclen`).
    `hz:417` is the **unique** surviving instance of this pattern in the CJK codecs.
  - Empirical corroboration: `repro/cjk_boundary_sweep.py` (all 20 CJK incremental
    decoders, single-byte + `~`/ESC-prefixed truncations, does NOT stop at first hit).
    Result so far: only `hz`/`b'~'` hits; gb2312/gbk/gb18030/... clean. Log:
    `logs/cjk_boundary_sweep.log`.
  - **DUPLICATE.** Open issue **python/cpython#157325** "codecs heap buffer overflow"
    (filed 2026-09-11T15:03Z) is the identical bug: same repro, same crash site
    `_codecs_cn.c:417`, same ASan trace. Fix already in progress: **PR #157333**
    "gh-157325: Fix an OOB read in the `hz` incremental decoder on a trailing `~`".
    => NOT a new finding. See `findings/DUPLICATE-001-hz-decoder-oob-read.md`.

- **Candidate 2 — `mmap` subscript-assignment OOB write via re-entrant `resize()`
  (`mmapmodule.c:406`).** Parent pattern `workflow-0137` (reentrant argument conversion
  invalidates a backing resource). Carried over from `audit2/FINDING-001`. Reproduced
  live on current HEAD: `mm[90000] = Evil()` where `Evil.__index__` calls `mm.resize(8)`
  → SEGV WRITE in `safe_byte_copy` via `mmap_ass_subscript_lock_held:1692`.
  - **DUPLICATE.** Open issue **python/cpython#157335** "mmap segfault"
    (filed 2026-09-11T16:59Z) is the identical bug: same repro, same crash site
    `mmapmodule.c:406`, same faulting address as `audit2`'s log.
    => NOT a new finding. See `findings/DUPLICATE-002-mmap-resize-reentrancy.md`.

- **Negative — sqlite `Blob` subscript with `__index__` that closes the blob**
  (`repro/repro_sqlite_blob_index_close.py`): raises `IndexError`, no ASan crash. The
  blob path re-validates (`CHECK_VALID`/index recompute) after the conversion. Not a bug.

- **Dedup methodology:** `gh search issues --repo python/cpython --include-prs` over
  hz_decode / _codecs_cn / cjkcodecs / MultibyteIncrementalDecoder / mmap resize /
  mmap subscript / mmap_ass_subscript / mmap __index__ terms; verified each near-hit by
  reading the issue body and comparing repro + crash site.

### Conclusion (this pass)

Both memory-safety defects that are confirmed and reproducible against current `main`
were independently reported upstream **on the same day (2026-09-11)** and now have open
issues (and a fix PR for the hz case). Under the task's own rule — check open issues,
do not file duplicates — there are **no new, confirmed, non-duplicate findings** to
write up in this pass. Work, reproducers, and full sanitizer output are retained below
and in `findings/` as duplicate-dispositioned records rather than novel reports. The
`cjk_boundary_sweep.py` run continues in the background as final corroboration that hz
is the only CJK-decoder boundary over-read.

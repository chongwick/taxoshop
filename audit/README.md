# CPython Sanitizer Audit — Summary

Structured audit of CPython `main` (@ `8f847875d60`, 3.16.0a0) against the
macro-taxonomy bug patterns in `taxos/macro_taxo`, using the repo `Dockerfile`
ASan+UBSan build. Full chronological log: `NOTES.md`.

## Result

**1 new, confirmed, non-duplicate finding.**

| ID | Title | Pattern | Sanitizer | Status |
|----|-------|---------|-----------|--------|
| [FINDING-001](findings/FINDING-001-hz-decoder-oob-read.md) | Heap OOB read in HZ incremental decoder (`hz_decode`, `_codecs_cn.c:417`) | workflow-0036 | ASan heap-buffer-overflow, READ size 1 | Confirmed, new |

## Method (maps to task steps)
1. **Read patterns + clustering** — `tally_bugs.py`, `macro_taxo/index.json`
   (163 patterns); studied wf-0003/0005/0007/0010/0022/0032/0036/0053/0061/0100/0155.
2. **Build** — `docker build --target asan-ubsan` (gcc 13.3.0, ASan+UBSan,
   `--without-pymalloc`). Plumbing validated with deliberate ASan + UBSan trips.
3. **Search source/docs for pattern-matching candidates** — targeted probes
   (`repro/targeted.py`) replaying historical instances = all clean (main guards
   them); focused malformed-input hunt (`repro/hunt.py`) across decoder surfaces
   still checkable under `-fno-strict-overflow`.
4. **Confirm with sanitizer build** — FINDING-001 reproduced deterministically;
   full reports in `findings/hz_asan.txt`, `findings/hz_asan_iterdecode.txt`.
5. **Dedupe vs open issues** — `gh search` (12 queries); no match.
6. **Write-up** — `findings/FINDING-001-...md` with root cause, repro, full
   sanitizer output, parent pattern, and fix.

## Layout
- `NOTES.md` — running notes / full audit trail.
- `repro/` — `run_suite_ubsan.sh`, `targeted.py`, `hunt.py`, `triage.py`,
  `repro_hz_min.py`, `repro_hz_stream.py`.
- `findings/` — write-ups + verbatim sanitizer logs.
- `logs/` — `docker-build.log`, `suite/` (regression-suite sanitizer artifacts).

## Negative results (documented, not speculative)
- Default regression suite under ASan+UBSan produced **no** new memory-safety
  findings — expected, as it is CPython's ASan-CI-covered path. Only artifact:
  a benign deliberate ~4EB allocation (test-driven, wf-0020 category) and
  ASan-slowdown timing flakiness in a few asyncio tests (wf-0042 category).
- Targeted replays of historically-fixed instances (float demotion, zero-count
  memcpy, native-handle ints, pickle signed-shift) are all guarded on `main`.
- `-fno-strict-overflow` in the build mutes gcc's signed-overflow/shift UBSan
  checks, dampening detectability of wf-0003 and some integer-overflow cases;
  weighting was toward alignment / bounds / nonnull / float-cast-overflow.

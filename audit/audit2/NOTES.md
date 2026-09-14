# CPython Sanitizer Audit — Running Notes

Started: 2026-09-11
Auditor: Claude Code
CPython commit under test: `8f847875d60` (3.16.0a0, remotes/origin/main, Sep 10 2026)
Sanitizer build: docker image `taxoshop/cpython-asan-ubsan:current`
  - ASan + UBSan, `--without-pymalloc`, `PYTHONMALLOC=malloc`
  - interpreter: `/src/cpython/python`
  - ASAN_OPTIONS=detect_leaks=0:abort_on_error=1:symbolize=1
  - UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1

## Method
1. Studied `taxos/macro_taxo` pattern write-ups + `tally_bugs.py` clustering.
2. Highest-yield reproducible families:
   - workflow-0137: reentrant user-code (`__index__`, `__len__`, `__bool__`, rich compare,
     iterators, callbacks) invalidates native state (frees/clears/resizes backing storage,
     detaches resource) while C holds a raw pointer/cached size → UAF / OOB / NULL deref.
   - workflow-0014 / 0080 / 0129: borrowed-handle / callback-reentrancy variants.
   - workflow-0003: signed left-shift UB (UBSan).
3. Grep current source for conversion/callback sites (`PyNumber_AsSsize_t`,
   `_PyEval_SliceIndex`, `PyNumber_Index`, `PyObject_IsTrue`, `PyObject_RichCompareBool`,
   `PyObject_Length`) that occur while a raw container pointer / cached size is live.
4. Confirm each candidate under the ASan/UBSan image with a minimal Python repro.
5. Check open CPython issues (gh) to avoid duplicates before writing up.

## Image note
`taxoshop/cpython-asan-ubsan:current` auto-fetches `origin/main` at build; it was
rebuilt mid-session (8f847875 -> e5d4fa28). Findings reproduce on current HEAD.

## Candidate log
(running list — status: IDEA / TESTING / CONFIRMED / DUP / FALSE)
- memoryview `__setitem__` reentrant release  — FALSE (CHECK_RELEASED re-check guards it)
- heapq siftup/siftdown reentrant `__lt__`    — FALSE (refreshes ob_item + size-change guard)
- array fromlist/setitem reentrant `__index__`— FALSE (CHECK_ARRAY_BOUNDS added in 143xxx sweep)
- **mmap subscript-assign reentrant resize()** — CONFIRMED (FINDING-001), not a dup
- mmap slice-assign reentrant `__buffer__`     — CONFIRMED (same root cause, Vector B)
- mmap READ subscript reentrant resize         — SAFE (size re-read after conv; IndexError) — negative test kept as scoping evidence (repro/mmap_read_negative.py)
- mmap write/read_byte/find/move               — SAFE (size re-read after their reentrancy point / clinic converts up front)
- _sqlite blob subscript reentrant close       — SAFE (blob_bytes re-read; sqlite null-checks closed handle)
- bytearray extend/setslice reentrant __buffer__— DUP/FIXED (gh-153578 re-clamps; corroborates mmap miss)
- array frombytes/extend reentrant __buffer__  — SAFE (old_size read after buffer acquired)
- ctypes Array ass_subscript reentrant __index__— SAFE (fixed-size arrays; can't resize)
- _bufferedreader/_bufferedwriter raw read/write— SAFE (return length bounds-checked n in [0,len])
- _elementtree element_[ass_]subscr slice      — SAFE/FIXED (gh-143200: slicelen computed after unpack)
- array_ass_subscr slice (RHS iterable)        — SAFE (RHS must be an array; no user reentrancy; ob_exports checked)
- CJK/all codec decode (20706 crafted/truncated probes) — no crash (framework REQUIRE_INBUF robust)
- CJK/all incremental decoders byte-by-byte (6426 probes) — no crash (prior HZ finding fixed)
- struct calcsize/pack_into overflow            — SAFE ("total struct size too long" guards)
- _pickle batch_list_exact / batch_dict_exact  — SAFE (GetItemRef strong refs / INCREF key+value before save; size guard)
- io.StringIO seek(2**62)+read pointer arith    — no UBSan report (gcc `-fsanitize=undefined` here doesn't flag OOB pointer *arithmetic*, only wraparound/real OOB access)

## Sanitizer coverage note
Build flags: `-fsanitize=address -fsanitize=undefined` (gcc). ASan catches real
OOB read/write + UAF (confirmed: mmap SEGV). This UBSan config catches
signed-overflow/shift/divide but NOT out-of-bounds pointer arithmetic that is never
dereferenced. So target ASan-catchable bugs (actual OOB/UAF) and signed-int UB.

## Scope exclusions
- **ctypes**: excluded per user direction. (It is documented as intentionally
  memory-unsafe; findings there are not meaningful.)

## Cross-reference corroboration
The `__buffer__`-resize class was fixed for bytearray.extend (gh-153578) and the
`__index__`-close case for mmap subscript READ (gh-103987), but mmap subscript
**assignment** was left uncovered for the **resize** variant — exactly FINDING-001.

## Confirmed findings
- FINDING-001: OOB write in `mmap` subscript/slice assignment via re-entrant `resize()`
  (workflow-0137). CHECK_VALID only detects close, not resize; bounds validated against
  stale size. Vectors: `value.__index__` (int index) and `value.__buffer__` (slice).

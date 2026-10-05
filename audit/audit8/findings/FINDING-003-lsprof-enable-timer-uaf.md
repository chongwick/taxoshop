# FINDING-003 — NEW: heap-use-after-free in _lsprof via reentrant `enable()` from the external timer

**Status:** CONFIRMED heap-UAF (ASan) + real heap corruption on vanilla build · **NEW** (distinct
from open #143545 and closed #121225) · pure Python, **no ctypes**.
**Parent pattern:** workflow-0080 (callback re-entrancy invalidates borrowed state/backing
storage) — the external timer callback re-enters the profiler and corrupts the C-side
`ProfilerContext` chain/freelist that the enclosing profiling event still uses.
**Build:** `taxoshop/cpython-asan-ubsan:current`, CPython 3.16.0a0 HEAD `e5d4fa28`; also a real
`malloc(): unaligned tcache chunk detected` abort on `cpython-vanilla:latest`.

## Summary
`_lsprof`'s external timer runs arbitrary Python via `CallExternalTimer`
(Modules/_lsprof.c:93) on every profiling event (function enter/leave), invoked from
`initContext` (:325) and `Stop` (:331). `Profiler.disable()` (:890) and `Profiler.clear()`
(:950) refuse to run while the timer is executing — they check the `POF_EXT_TIMER` flag and
raise `RuntimeError`. **`Profiler.enable()` (:806) has no such guard.**

Calling `enable()` from inside the timer, while the profiler is active, re-registers the
`sys.monitoring` callbacks and resets tool state mid-event. This corrupts the `ProfilerContext`
bookkeeping (the `currentProfilerContext` chain and `freelistProfilerContext`) that
`ptrace_enter_call` (:358), `Stop`, and `flush_unmatched` (:862) manage. A subsequent
`disable()` → `flush_unmatched` then `PyMem_Free`s a `ProfilerContext` that is still referenced,
yielding a heap use-after-free.

## Root cause
`enable()` is missing the `POF_EXT_TIMER` reentrancy guard that `disable()`/`clear()` carry, so
the profiler's internal state can be reconfigured from within a profiling callback. The
`ProfilerContext` objects are `PyMem_Malloc`ed (ASan-instrumented), so the dangling use is
caught precisely:
- **allocated** at `ptrace_enter_call` Modules/_lsprof.c:388 (`PyMem_Malloc(sizeof(ProfilerContext))`)
- **freed** at `flush_unmatched` Modules/_lsprof.c:873 (via `_lsprof_Profiler_disable_impl:930`)
- **used (READ)** at `ptrace_enter_call` Modules/_lsprof.c:383 (`pObj->freelistProfilerContext = pContext->previous`)

## Reproducer (pure Python, no ctypes) — `repro/t_lsprof_enable_uaf.py`
```python
import _lsprof
prof = _lsprof.Profiler()
def evil_timer():
    try:
        prof.enable()          # reentrant, UNGUARDED (unlike disable()/clear())
    except Exception:
        pass
    return 0
prof.__init__(timer=evil_timer)
prof.enable()
def foo():
    return 1
foo()                          # one profiled call: timer fires -> enable() corrupts state
prof.disable()                 # frees a still-referenced ProfilerContext -> use-after-free
```
Deterministic: 3/3 ASan aborts. A single profiled call + `disable()` suffices. (Without the
final `disable()` the corrupted context is not walked/freed, so `disable()` — or profiler
teardown at dealloc, which also calls `flush_unmatched`+`clearEntries` — is what surfaces the
free.)

## Sanitizer output (logs/lsprof_enable_uaf.asan.txt)
```
==ERROR: AddressSanitizer: heap-use-after-free ... READ of size 8
    #0 ptrace_enter_call Modules/_lsprof.c:383
    #1 _lsprof_Profiler__ccall_callback_impl Modules/_lsprof.c:733
freed by thread T0 here:
    #1 flush_unmatched Modules/_lsprof.c:873
    #2 _lsprof_Profiler_disable_impl Modules/_lsprof.c:930
previously allocated by thread T0 here:
    #1 ptrace_enter_call Modules/_lsprof.c:388
SUMMARY: AddressSanitizer: heap-use-after-free Modules/_lsprof.c:383 in ptrace_enter_call
```
Vanilla (non-sanitizer) `cpython-vanilla:latest`: prints `no crash` then aborts with
`malloc(): unaligned tcache chunk detected` (exit 134) — confirming real heap corruption, not a
sanitizer-only artifact.

## Duplicate analysis — NEW (distinct from the known lsprof timer UAFs)
- **#143545 (OPEN)** "Use-after-free in lsprof `initContext` via re-entrant external timer
  `__index__`" — DISTINCT. Its trigger is a timer whose **`__index__`** calls `prof.clear()`,
  exploiting that `clear()`'s `POF_EXT_TIMER` guard is bypassable in the **result-conversion
  window** (after `CallExternalTimer` clears the flag at :101, `_PyTime_FromSecondsObject` runs
  `__index__`). Free is via `clearEntries`; crash is in `initContext`. My bug's trigger is a
  direct `enable()` call **while the flag is set** — `enable()` simply has **no guard at all** —
  free is via `flush_unmatched` (disable), crash is in `ptrace_enter_call:383`. A fix that only
  closes the `clear()`/conversion-window hole would not cover the unguarded `enable()` path.
- **#121225 (CLOSED, 3.12–3.14)** "Use After Free in Stop(_lsprof.c)" — the older Stop-path UAF,
  addressed by the `POF_EXT_TIMER` guards that are present on HEAD (on disable/clear). My finding
  is a residual gap in that hardening (enable left unguarded), reproducing on HEAD `e5d4fa28`.
- `git log -8000`: no fix guarding `enable()` against external-timer reentrancy.

## Suggested fix direction (for the report, not applied here)
Add the same `POF_EXT_TIMER` check to `_lsprof_Profiler_enable_impl` (and, per #143545, also
guard the timer result-conversion window / re-apply the flag around
`_PyTime_FromSecondsObject`/`PyLong_AsInt64`), so no profiler control method (enable/disable/
clear/__init__) can run while a profiling callback is on the stack.

# FINDING-005 — Write-write race on shared static exception types during concurrent subinterpreter init

- **Parent pattern:** workflow-0077 (concurrent contexts race on shared process-wide state) — Sites 3 & 9.
- **Status:** CONFIRMED (TSan, free-threaded build). **Already reported upstream: python/cpython#129824 (OPEN)** — "Various data races in subinterpreter tests under TSAN." Re-find, not new.

## Root cause
Creating a subinterpreter runs `_PyExc_InitTypes` (`Objects/exceptions.c:4555`), which walks
the process-global `static_exceptions[]` table and, per entry, writes into the **shared
static** type object:

```c
exc->tp_vectorcall = BaseException_vectorcall;   // exceptions.c:4566
```

The `static_exceptions[].exc` objects are process-global statics shared by all interpreters.
When two OS threads each create a subinterpreter concurrently, both execute this loop and
write the same `exc->tp_vectorcall` slot with no synchronization → write-write data race on
process-global type metadata (`_PyStaticType_InitBuiltin` in the same loop touches shared
static-type bookkeeping as well).

## Reproducer (`repro/tsan/t_wf0077_s3_subinterp_intern.py`, no ctypes)
```python
import _interpreters as I, threading
code = 'import sys\nfor _ in range(2000): sys.intern("novelstring_zx")'
def run():
    sub = I.create()
    try: I.run_string(sub, code)
    finally:
        try: I.destroy(sub)
        except Exception: pass
ts = [threading.Thread(target=run) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
```
(The race fires during the concurrent `I.create()` subinterpreter initialization.)

## Sanitizer output (full log `logs/wf0077_s3_subinterp.tsan.txt`)
```
WARNING: ThreadSanitizer: data race
  Write of size 8 by thread T2:
    #0 _PyExc_InitTypes Objects/exceptions.c:4566
    #1 pycore_init_types Python/pylifecycle.c:798
    #2 pycore_interp_init Python/pylifecycle.c:981
  Previous write of size 8 by thread T1:
    #0 _PyExc_InitTypes Objects/exceptions.c:4566
SUMMARY: ThreadSanitizer: data race Objects/exceptions.c:4566 in _PyExc_InitTypes
```
(7 distinct races reported, incl. `_PyXI_InitTypes` crossinterp.c:3240 on the same run.)

## Duplicate analysis
- **#129824 — OPEN** (labels: interpreter-core, topic-subinterpreters, type-bug). Umbrella
  for TSAN-reported races in shared type metadata / exception aliases / interned objects
  across concurrent subinterpreters. This `_PyExc_InitTypes` `tp_vectorcall` write is one of
  those shared-static-type races.

## Relationship to macro-taxonomy
workflow-0077: a process-global table (`static_exceptions`) and shared static type objects
are initialized by two concurrent contexts with no once-only / locked publication protocol.
</content>

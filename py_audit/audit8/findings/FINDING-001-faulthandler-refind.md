# FINDING-001 — faulthandler watchdog lock-handshake race (RE-FIND of open #151475)

**Status:** CONFIRMED crash · **DUP of upstream #151475 (OPEN)** · NOT a new finding.
**Parent pattern:** workflow-0077 Site 8 (concurrent contexts race on shared process-wide state).
**Build:** free-threaded TSan image `taxoshop/cpython-tsan-ft:current` (Py_GIL_DISABLED=1),
CPython 3.16.0a0 HEAD `e5d4fa28`. Clean on the GIL ASan build (FT-only).

## Root cause
`Modules/faulthandler.c` mutates its process-global watchdog state
(`_PyRuntime.faulthandler.thread`) with no lock protecting the whole arm/cancel sequence.
The `dump_traceback_later` / `cancel_dump_traceback_later` / `faulthandler_thread` handshake
uses two `PyThread_type_lock`s and *assumes a single orchestrating thread* holds
`thread.cancel_event`:

- `dump_traceback_later_impl` (Modules/faulthandler.c:797) lazily allocates `thread.running`
  (:839) and `thread.cancel_event` (:846), then calls `cancel_dump_traceback_later()`.
- `cancel_dump_traceback_later` (:727) does `PyThread_release_lock(thread.cancel_event)` (:736),
  waits on `thread.running`, then `PyThread_acquire_lock(thread.cancel_event, 1)` (:743), and
  `PyMem_Free(thread.header)` (double-free hazard under concurrency).

With the GIL disabled, two threads racing arm/cancel break the handshake: `release`/`acquire`
of `cancel_event`/`running` happen from the wrong thread, so a lock is released that the
releasing thread does not hold → `PyMutex_Unlock: unlocking mutex that is not locked` abort.
Two threads can also both see `cancel_event == NULL` and both allocate it (one leaks).

## Reproducer (pure Python, NO ctypes)
`repro/tsan/t_0077s8_fh_min.py` — two threads, each looping one *documented public* API:

```python
import faulthandler, threading, os, time
devnull = open(os.devnull, "w"); stop = threading.Event()
def rearm():
    while not stop.is_set():
        try: faulthandler.dump_traceback_later(0.001, file=devnull)
        except Exception: pass
def cancel():
    while not stop.is_set(): faulthandler.cancel_dump_traceback_later()
a = threading.Thread(target=rearm); b = threading.Thread(target=cancel)
a.start(); b.start(); time.sleep(5); stop.set(); a.join(); b.join()
```

`repro/tsan/t_0077s8_faulthandler.py` — broader variant also racing enable()/disable().

## Observed
```
Fatal Python error: PyMutex_Unlock: unlocking mutex that is not locked
Python runtime state: initialized
Stack (most recent call first):
  File ".../t_0077s8_fh_min.py", line 11 in rearm   (= faulthandler.dump_traceback_later)
```
Exit 134 on the FT build (logs/fh_min.tsan.txt). Exit 0 / clean on the GIL ASan build
(logs/fh_min.asan.txt).

## Duplicate analysis — DUP, do not re-file
Upstream **#151475 (OPEN)** "faulthandler: data races in enable()/disable() and
dump_traceback_later() under free threading" — its **Bug 2** is exactly this watchdog
lock-handshake race, with the identical `PyMutex_Unlock` crash and an equivalent
arm-vs-cancel reproducer. (That issue was itself drafted by Claude Code / devdanzin.)
The enable()/disable() non-atomic `enabled` flag race is tracked in **#151363**.
This is a successful *re-find* of a confirmed real open bug (cf. audit6's zoneinfo #142782 /
OrderedDict #142637 re-finds), not a new report.

## Relationship to the macro-taxonomy
Textbook workflow-0077: a process-global (`_PyRuntime.faulthandler.thread` + its two
`PyThread_type_lock`s) is mutated and consumed from multiple contexts without a complete
synchronization/publication protocol. Distinct from the libc-static-buffer 0077 sites
(strerror/getlogin/ttyname/environ) which are real races but live in uninstrumented libc
memory and are therefore not sanitizer-confirmable.

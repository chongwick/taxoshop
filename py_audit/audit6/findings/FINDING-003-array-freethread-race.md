# FINDING-003 — Data race in `array` (append write vs tobytes read of `ob_item`)

- **Parent pattern:** workflow-0081 (concurrent unsynchronized access to shared mutable storage) — Site 10.
- **Status:** CONFIRMED (TSan, free-threaded build). **Already reported upstream: python/cpython#128942 (OPEN)** — "Python `array` module is not free-thread safe." The thread-safety PR gh-128943 was **reverted** (#130707) for a scimark perf regression, so the module is knowingly unsafe on HEAD. Re-find, not new.

## Root cause
On a free-threaded build, `array.array` methods do not hold a common per-object lock. Two
threads sharing one array — one appending, one serializing — race the raw `ob_item` buffer:

- **Writer:** `array.append` → `array_array_append_impl` (`arraymodule.c:1544`) → `ins`
  (`:1289`) → `ins1` (`:844`) → `i_setitem` (`:398`) writes an element into `ob_item`
  (and `ins1` may `realloc` `ob_item`).
- **Reader:** `array.tobytes` → `array_array_tobytes_impl` (`arraymodule.c:1934`) →
  `PyBytes_FromStringAndSize` `memcpy`s the whole `ob_item` buffer.

Neither path takes a critical section, so the memcpy read races the element store (and, on a
growth step, the freed/moved old buffer → potential UAF).

## Reproducer (`repro/tsan/t_wf0081_s10_array.py`, no ctypes)
```python
import threading, array
a = array.array('i', range(1000))
stop = False
def grower():
    for _ in range(20000):
        a.append(1)
        if len(a) > 5000: del a[1000:]
def reader():
    while not stop:
        try: _ = a[0]; _ = a.tobytes()
        except Exception: pass
r = threading.Thread(target=reader); r.start()
g = threading.Thread(target=grower); g.start()
g.join(); stop = True; r.join()
```

## Sanitizer output (full log `logs/wf0081_s10_array.tsan.txt`)
```
WARNING: ThreadSanitizer: data race
  Read of size 4 by thread T1:
    #1 PyBytes_FromStringAndSize Objects/bytesobject.c:157
    #2 array_array_tobytes_impl Modules/arraymodule.c:1934
  Previous write of size 4 by thread T2:
    #0 i_setitem Modules/arraymodule.c:398
    #1 ins1 Modules/arraymodule.c:844
    #3 array_array_append_impl Modules/arraymodule.c:1544
SUMMARY: ThreadSanitizer: data race in __tsan_memcpy
```
(8 distinct races reported across the run.)

## Duplicate analysis
- **#128942 — OPEN** ("array module is not free-thread safe"); gh-128943 fix reverted by
  **#130707 (MERGED)** for performance. No current protection on HEAD `e5d4fa28`.

## Relationship to macro-taxonomy
workflow-0081: aliases to one mutable backing store (`ob_item`) are read/written from two
threads with no single lock; a grow-realloc under the reader is the sharper UAF variant.
</content>

# FINDING-004 — Data race on a shared `dict` iterator cursor under free-threading

- **Parent pattern:** workflow-0081 (concurrent unsynchronized access to shared mutable state) — Site 6.
- **Status:** CONFIRMED (TSan, free-threaded build). **Already reported upstream: python/cpython#154130 (OPEN)** — "Sharing a dict iterator across threads double-DECREFs `di_dict` under free-threading." Re-find, not new.

## Root cause
All three dict iterators route `next()` through `dictiter_iternext_threadsafe`
(`Objects/dictobject.c`). The iterator's own cursor / owning-dict fields are mutated without
protecting them against a second thread advancing the *same* iterator object:

- **Read:** `dictiter_iternextkey` (`dictobject.c:5784`) reads the shared cursor/state.
- **Write:** `dictiter_iternext_threadsafe` (`dictobject.c:6158`) writes it.

Two threads calling `next(it)` on one shared iterator race that field; the exhaustion path
also drops the iterator's owning reference to the dict, so the race can become a
double-DECREF of `di_dict` (the crash reported in #154130).

## Reproducer (`repro/tsan/t_wf0081_s6_dict_iter.py`, no ctypes)
```python
import threading
d = {i: i for i in range(1000)}
it = iter(d)
def worker():
    while True:
        try: next(it)
        except StopIteration: break
        except Exception: break
ts = [threading.Thread(target=worker) for _ in range(6)]
for t in ts: t.start()
for t in ts: t.join()
```

## Sanitizer output (full log `logs/wf0081_s6_dict_iter.tsan.txt`)
```
WARNING: ThreadSanitizer: data race
  Write of size 8 by thread T2:
    #0 dictiter_iternext_threadsafe Objects/dictobject.c:6158
    #1 dictiter_iternextkey Objects/dictobject.c:5791
  Previous read of size 8 by thread T1:
    #0 dictiter_iternextkey Objects/dictobject.c:5784
SUMMARY: ThreadSanitizer: data race Objects/dictobject.c:6158 in dictiter_iternext_threadsafe
```

## Duplicate analysis
- **#154130 — OPEN** (labels: interpreter-core, topic-free-threading, type-crash). Exactly
  this: shared dict iterator across threads → cursor race → double-DECREF `di_dict` / crash.
  Related family member #144356 (set iterator) was fixed; the dict/list iterators are the
  adjacent unfixed variant flagged by the hypothesis.

## Relationship to macro-taxonomy
workflow-0081: an iterator's cached cursor + borrowed container pointer are shared and
mutated by two threads with only container-level (not iterator-level) protection.
</content>

# FINDING-001 — Heap use-after-free in `find_in_strong_cache` via re-entrant `ZoneInfo.clear_cache()`

- **Parent pattern:** workflow-0080 (callback re-entrancy invalidates borrowed state) — Site 1 (flagship).
- **Status:** CONFIRMED (ASan). **Already reported upstream: python/cpython#142782 (OPEN, unfixed on HEAD).** This is a *re-find* of a known-but-unfixed bug, not a new report.

## Root cause
`find_in_strong_cache()` (`Modules/_zoneinfo.c:2437`) walks the per-type strong-cache
linked list holding a raw `node` pointer:

```c
const StrongCacheNode *node = root;
while (node != NULL) {
    int rv = PyObject_RichCompareBool(key, node->key, Py_EQ);  // :2441 runs user __eq__
    ...
    node = node->next;                                         // :2449 UAF
}
```

`key` is the **left** operand, so `key.__eq__` runs arbitrary Python *while the raw `node`
pointer is live*. On the GIL build the `@critical_section` on `ZoneInfo.__new__` is a no-op,
so `__eq__` can re-enter `ZoneInfo.clear_cache()`, which frees every `StrongCacheNode`
(`strong_cache_node_free` :2382 ← `clear_strong_cache` :2588 ← `zoneinfo_ZoneInfo_clear_cache_impl` :523).
When the compare returns, `node = node->next` dereferences the freed node → heap-UAF.

Call chain: `zoneinfo_ZoneInfo_impl` :319 → `zone_from_strong_cache` :2526 → `find_in_strong_cache` :2449.

## Reproducer (`repro/wf0080_s1_zoneinfo.py`, no ctypes)
```python
from zoneinfo import ZoneInfo
class Evil(str):
    def __eq__(self, other):
        ZoneInfo.clear_cache()      # frees every StrongCacheNode mid-traversal
        return False
    __hash__ = str.__hash__
ZoneInfo("America/New_York"); ZoneInfo("Europe/London"); ZoneInfo("Asia/Tokyo")
ZoneInfo(Evil("America/New_York"))  # node=node->next reads freed memory -> UAF
```

## Sanitizer output (full log `logs/wf0080_s1_zoneinfo.asan.txt`)
```
==1==ERROR: AddressSanitizer: heap-use-after-free ... READ of size 8
    #0 find_in_strong_cache Modules/_zoneinfo.c:2449
    #1 zone_from_strong_cache Modules/_zoneinfo.c:2526
    #2 zoneinfo_ZoneInfo_impl Modules/_zoneinfo.c:319
freed by thread T0 here:
    #1 strong_cache_node_free Modules/_zoneinfo.c:2382
    #3 clear_strong_cache Modules/_zoneinfo.c:2588
    #5 zoneinfo_ZoneInfo_clear_cache_impl Modules/_zoneinfo.c:523
SUMMARY: AddressSanitizer: heap-use-after-free Modules/_zoneinfo.c:2449 in find_in_strong_cache
```

## Duplicate analysis
- **python/cpython#142782 — OPEN.** Title: "Use-after-free in `zone_from_strong_cache` via
  re-entrant `ZoneInfo.clear_cache()` from key `__eq__`". Exactly this bug; this finding
  re-confirms it on HEAD `e5d4fa28`.
- `gh-142783` (commit 8307a14d0ed) fixed a **different** UAF — the `weak_cache` borrowed-ref
  lifetime in `get_weak_cache`/`zoneinfo_ZoneInfo_impl`. It does not touch
  `find_in_strong_cache` or the strong-cache node traversal.
- `gh-142763`/`gh-142781` fixed weak-cache race / type-confusion, also unrelated.

## Relationship to macro-taxonomy
Textbook workflow-0080: a native fast path holds a borrowed raw pointer (`node`) across a
user-defined callback (`__eq__`), which re-enters and frees the backing storage before the
operation resumes.
</content>

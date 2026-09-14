# FINDING-002 — Heap use-after-free in OrderedDict node ops via re-entrant key `__eq__`

- **Parent pattern:** workflow-0080 (callback re-entrancy invalidates borrowed state) — Site 7.
- **Status:** CONFIRMED (ASan) on two entry points: `move_to_end()` and `pop()`.
  **Already reported upstream: python/cpython#142637 (OPEN)** and its `pop`-specific sibling
  **#154817 (OPEN)**. Re-find of a known-but-unfixed bug (only `copy()` was fixed by gh-148660).

## Root cause
OrderedDict locates a key via `_odict_find_node` → `_odict_get_index` →
`_odict_get_index_raw` (`Objects/odictobject.c:549`), which calls the underlying
`_Py_dict_lookup`. For colliding keys the lookup runs `PyObject_RichCompareBool` →
user `__eq__`. A re-entrant `__eq__` that calls `od.clear()` frees the OrderedDict's
`od_fast_nodes` array (via dict `clear_lock_held` ← `OrderedDict_clear_impl:1225`).
When the lookup returns, `_odict_get_index_raw:549` reads the freed fast-nodes array → UAF.

Confirmed call chains:
- `OrderedDict_move_to_end_impl:1351` → `_odict_find_node:645` → `_odict_get_index:614` → `_odict_get_index_raw:549`.
- `OrderedDict.pop` (same `_odict_find_node`/`_odict_get_index_raw` path).

## Reproducer (`repro/battery/t_wf0080_s7_ordereddict.py` and `..._s7b_odict_pop.py`, no ctypes)
```python
from collections import OrderedDict
class Evil:
    def __hash__(self): return 1          # force collision chain -> eq is called
    def __eq__(self, other):
        od.clear()                        # frees od_fast_nodes mid-lookup
        return False
od = OrderedDict()
for i in range(8): od[Evil()] = i
od.move_to_end(Evil())                    # (or od.pop(Evil())) -> UAF
```

## Sanitizer output (full logs `logs/wf0080_s7_ordereddict.asan.txt`, `logs/wf0080_s7b_odict_pop.asan.txt`)
```
==1==ERROR: AddressSanitizer: heap-use-after-free ... READ of size 8
    #0 _odict_get_index_raw Objects/odictobject.c:549
    #1 _odict_get_index Objects/odictobject.c:614
    #2 _odict_find_node Objects/odictobject.c:645
    #3 OrderedDict_move_to_end_impl Objects/odictobject.c:1351
freed by thread T0 here:
    #1 clear_lock_held Objects/dictobject.c:3149
    #2 OrderedDict_clear_impl Objects/odictobject.c:1225
    ... slot_tp_richcompare (evil __eq__ -> od.clear())
SUMMARY: AddressSanitizer: heap-use-after-free Objects/odictobject.c:549 in _odict_get_index_raw
```

## Duplicate analysis
- **#142637 — OPEN.** "Use-after-free in several `OrderedDict` operations via re-entrant
  `__eq__`", explicitly lists `move_to_end` and `pop`.
- **#154817 — OPEN.** "OrderedDict.pop() can segfault when key equality changes between lookups."
- `gh-148660` (commit 7d128e319f3) fixed only `OrderedDict.copy()` reentrant UAF; the
  `move_to_end`/`pop`/`__delitem__` paths remain unfixed on HEAD `e5d4fa28`.

## Relationship to macro-taxonomy
workflow-0080: a native mapping op caches a raw node/index pointer across an equality
callback that re-enters and frees the backing node array.
</content>

# Finding 02 — Use-after-free in `OrderedDict._odict_find_node` family, reached via `move_to_end()`

> **⚠️ DEDUP RESULT: DUPLICATE — NOT A NOVEL FINDING (determined by sanitizer crash location).**
> Dedup is decided by the crashing stack frame. This finding's crash location is
> `SUMMARY: AddressSanitizer: heap-use-after-free Objects/odictobject.c:550 in _odict_get_index_raw`
> (`#0 _odict_get_index_raw odictobject.c:550`). **[gh_142637](../taxos/micro_taxo/gh_142637.md)**
> records the *identical* crash location — its Full Sanitizer Output ends in
> `SUMMARY: AddressSanitizer: heap-use-after-free Objects/odictobject.c:550 in _odict_get_index_raw`.
> The two differ only in the *caller* path below the faulting frame (this finding: `move_to_end` →
> `_odict_find_node`; gh_142637: `del` → `_odict_clear_node` → `PyODict_DelItem`), but the `#0`
> faulting frame is the same, so they are **the same bug**. (Distinct from
> [gh_142734](../taxos/micro_taxo/gh_142734.md), which crashes at `odictobject.c:1276` in
> `OrderedDict_copy_impl` — a different location.) Retained as audit trail; **excluded from the
> confirmed-novel-findings list.**

- **Component:** `Objects/odictobject.c` (C `collections.OrderedDict`)
- **Bug class:** heap-use-after-free (read)
- **Detection:** AddressSanitizer, on CPython `f5394c257ce` (3.15.0a1), default GIL build
- **Macro taxonomy:** [Re-entrant callbacks and protocol methods](../taxos/macro_taxos/reentrant_callbacks.md)
  (also [Lifetime and teardown ordering](../taxos/macro_taxos/lifetime_and_teardown.md): a Python
  callback runs `clear()` and frees a container's backing store while a native frame still holds a
  raw alias into it).
- **Relation to recorded taxonomy:** micro-taxo
  [#142637](../taxos/micro_taxos/gh_142637.md) records "use-after-free in *several* `OrderedDict`
  operations via re-entrant `__eq__`", but its single reproducer is `del od[Trigger()]` (the
  `__delitem__`/`pop` path through `_odict_popkey_hash`). This finding is the **`move_to_end()`
  trigger** — a *non-deleting, reordering* public method that reaches the same faulting site
  through a **different call chain** (`OrderedDict_move_to_end_impl` → `_odict_find_node`). It is an
  adjacent trigger the recorded reproducer does not exercise, and it confirms that the vulnerable
  primitive is `_odict_find_node`/`_odict_get_index_raw`, not the delete path specifically.

## Root cause

Every `OrderedDict` key lookup funnels through `_odict_get_index_raw`, which snapshots the dict's
key table **before** performing the lookup that may run Python code:

```c
static Py_ssize_t
_odict_get_index_raw(PyODictObject *od, PyObject *key, Py_hash_t hash)
{
    ...
    PyDictKeysObject *keys = ((PyDictObject *)od)->ma_keys;   /* snapshot BEFORE lookup */
    Py_ssize_t ix;
    ix = _Py_dict_lookup((PyDictObject *)od, key, hash, &value);  /* runs __eq__ (re-entrancy) */
    if (ix == DKIX_EMPTY) {
        return keys->dk_nentries;   /* <-- keys may be freed here */
    }
    ...
}
```
(`Objects/odictobject.c:536-556`; the freed read is `keys->dk_nentries` at `:550`.)

`_Py_dict_lookup` compares the probed key against stored keys via `PyObject_RichCompareBool`. If a
stored key's `__eq__` calls `od.clear()`, then `OrderedDict_clear` →
`_odict_clear_nodes` frees `od_fast_nodes` and every node, and clearing the dict frees the **old
`ma_keys`** object that the local `keys` pointer still aliases. When the interrupted lookup then
resolves to `DKIX_EMPTY` (the dict is now empty), the function dereferences the freed
`keys->dk_nentries` → use-after-free.

This snapshot-then-callback hazard is unguarded: unlike `_odict_keys_equal` (which re-checks
`od_state` after each compare, `Objects/odictobject.c:847`), the `_odict_find_node` path has **no
post-callback re-validation**. Every caller of `_odict_find_node` / `_odict_find_node_hash` is
therefore exposed — including `move_to_end()`, which uses it and then dereferences the returned node:

```c
node = _odict_find_node(self, key);       /* Objects/odictobject.c:1336 */
if (node == NULL) { ... }
if (node != _odict_LAST(self)) {
    _odict_remove_node(self, node);        /* would also touch a freed node */
    _odict_add_tail(self, node);
}
```

## Trigger (re-entrant-callback macro pattern)

1. Native `move_to_end` calls `_odict_find_node(self, key)` — the re-entrancy boundary.
2. Inside, `_Py_dict_lookup` compares `key` against a **hash-colliding** stored key, invoking that
   key's Python `__eq__`.
3. `__eq__` calls `od.clear()`, freeing the nodes, `od_fast_nodes`, and the old `ma_keys`.
4. The interrupted lookup returns `DKIX_EMPTY`; `_odict_get_index_raw` reads the freed
   `keys->dk_nentries`.

## Reproducer

`findings/repros/od_move_to_end_uaf.py`:

```python
from collections import OrderedDict

class K:
    def __hash__(self): return 1
    def __eq__(self, other):
        od.clear()      # free all nodes + od_fast_nodes + old ma_keys during the lookup
        return True

od = OrderedDict()
od[K()] = 0            # stored key with hash 1
od[object()] = 1       # keep od non-empty (object() has a different hash, so setup is stable)
od.move_to_end(K())    # a fresh K() with hash 1 -> collision -> stored K.__eq__ clears od mid-lookup
```

The second key deliberately has a *different* hash so the `__eq__` bomb stays dormant during setup;
`move_to_end(K())` introduces a hash-1 collision that forces the destructive comparison.

## Sanitizer evidence

Full log: `findings/logs/od_move_to_end_uaf.asan.txt`

```
==898==ERROR: AddressSanitizer: heap-use-after-free on address 0x50e000012038
READ of size 8 at 0x50e000012038 thread T0
    #0 _odict_get_index_raw Objects/odictobject.c:550
    #1 _odict_get_index Objects/odictobject.c:615
    #2 _odict_find_node Objects/odictobject.c:646
    #3 OrderedDict_move_to_end_impl Objects/odictobject.c:1336
    #4 OrderedDict_move_to_end Objects/clinic/odictobject.c.h:448
    ...
freed by thread T0 here:
    #1 OrderedDict_clear_impl Objects/odictobject.c:1226
    #2 OrderedDict_clear Objects/clinic/odictobject.c.h:353
    ...
    vectorcall_unbound Objects/typeobject.c:3034   (the re-entrant __eq__)
```

## Additional confirmed trigger (same root site)

`od.pop(K())` reaches `:550` through `_odict_popkey_hash` → `_odict_find_node_hash`
(`findings/probes/od_iter_find.py`, ASan `heap-use-after-free` at the same address). This is the
`_odict_popkey_hash` variant of the recorded `del` reproducer and is shown here only to pin the
shared root cause; `move_to_end` is the novel, non-deleting trigger.

## Not affected (checked this session)

- `OrderedDict.setdefault(K(), ...)` — no crash. The found-key path INCREFs the value immediately;
  the not-found path re-does the insertion after the callback without reusing a stale alias.

## Suggested fix

Re-validate after the re-entrant lookup in `_odict_get_index_raw` (or in `_odict_find_node*`): after
`_Py_dict_lookup` returns, reload `((PyDictObject *)od)->ma_keys` instead of using the pre-lookup
`keys` snapshot, and have callers treat a mutated `od_state`/emptied table as "not found" (mirroring
the `od_state` guard already used in `_odict_keys_equal`). The minimal fix for the `DKIX_EMPTY`
branch is to read `dk_nentries` from the *current* `ma_keys`, not the captured `keys`.

## Notes / limitations

- The freed access is a read on the `DKIX_EMPTY` branch; it is a genuine memory-safety defect,
  trivially reachable from pure Python, on a default (GIL) build.
- The faulting instruction is shared with the recorded `del`/`pop` reproducer of #142637; the
  novelty is the **`move_to_end` public-API trigger** (a reordering operation, not a deletion) plus
  the explicit identification of `_odict_get_index_raw`'s pre-lookup `keys` snapshot as the exact
  unguarded site.

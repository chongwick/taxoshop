# workflow-0080 — Callback re-entrancy invalidates borrowed state or backing storage

> A native fast path holds unowned references / raw pointers / cached sizes across a
> user-defined callback (hash, equality, str, iteration), which re-enters and mutates/clears/
> frees that state before the operation resumes.

10 fresh sites. All single-thread; testable on the GIL ASan/UBSan image (`@critical_section`
is a no-op there).

---

## Site 1 — `memoryview.__contains__` / `.count` compare-loop reentrant mutation  ⭐

**Site.** `memory_count` (`Objects/memoryobject.c:2904`) and the `__contains__` path iterate the
view calling `PyObject_RichCompareBool(item, value, Py_EQ)` per element while walking the
buffer.

**Reasoning.** `value.__eq__` runs Python each iteration. If it mutates the exporting object or
`release()`s the view, the loop keeps reading buffer items whose backing has changed/gone.

**Why it fits.** Borrowed buffer view held across an equality callback that invalidates it.

**Reachability.** `value in memoryview(bytearray(...))` / `mv.count(Evil())`.

**Trigger hypothesis.** `Evil.__eq__` calls `mv.release()` or (for a non-pinning exporter) frees
the exporter, then the loop's next item read faults.

**Confidence & dup-check.** Medium. See workflow-0014 Site 1 (same code, release variant).
Compare any `gh` "memoryview contains" issues; bytearray exporters are pinned (BufferError on
resize) so the release path is the sharp one.

---

## Site 2 — `_PySequence_IterSearch` generic `in` / `index` / `count`

**Site.** `_PySequence_IterSearch` (`Objects/abstract.c:2175`) loops
`item = PyIter_Next(it); cmp = PyObject_RichCompareBool(item, obj, Py_EQ)` for any non-fast
sequence, holding the borrowed iterator `it` across `obj.__eq__`.

**Reasoning.** `obj.__eq__` can exhaust/close the iterator, or free the underlying sequence, or
re-enter the same operation. `it` is held (with a ref) but the *sequence it iterates* may be a C
object whose storage `__eq__` frees.

**Why it fits.** Borrowed iteration state + the searched sequence held across an equality
callback.

**Reachability.** `obj in some_seq` for a sequence without a C `sq_contains` fast path;
`obj.__eq__` mutates `some_seq`.

**Trigger hypothesis.** A custom sequence backed by a C buffer; `obj.__eq__` shrinks/frees that
buffer; `PyIter_Next` then reads freed storage.

**Confidence & dup-check.** Low-medium. `it` is owned; the risk is only for sequences whose
iterator caches a raw pointer. Ruling-out lead for most builtins.

---

## Site 3 — `set` / `frozenset` update & intersection rehash during `__hash__`

**Site.** `set_update_internal` (`Objects/setobject.c:1772`) and `set_intersection` loop
`key = PyIter_Next(it); hash = PyObject_Hash(key); set_contains_entry(so, key, hash)`, and
`set_merge`/`set_next` walk `so->table` with a raw `entry` pointer.

**Reasoning.** `key.__hash__` runs Python and can add to / clear `so`, triggering a table
resize (`set_table_resize`) that frees the `entry`/`table` a surrounding walk holds.

**Why it fits.** Borrowed hash-table `entry`/`table` pointer held across a `__hash__` callback
that reshapes the same set — the `#142637` mechanism on `set`.

**Reachability.** `so |= iterable` / `so &= other` where elements' `__hash__` mutate `so`.

**Trigger hypothesis.** `Evil.__hash__` calls `so.clear()` (frees table) then returns a constant;
the next `set_add_entry`/`set_next` uses the freed table.

**Confidence & dup-check.** Medium. Set is broadly hardened but the update/intersection
`__hash__`-reentrancy is worth re-checking. Confirm resize can't run under the op's lock on the
GIL build (it can).

---

## Site 4 — `deque.__eq__` / `__lt__` element compare mutates the deque

**Site.** `deque_richcompare` (`Modules/_collectionsmodule.c:1700`) advances two deque iterators
(`it1`, `it2`) and compares elements with `PyObject_RichCompareBool`, holding borrowed `block`
pointers into each deque's linked-block storage.

**Reasoning.** An element's `__eq__` can `clear()`/`append()`/`popleft()` a deque being
compared, freeing the `block` the iterator cursor points into.

**Why it fits.** Borrowed block-list cursor held across an equality callback that frees blocks.

**Reachability.** `d1 == d2` where an element's `__eq__` mutates `d1`.

**Trigger hypothesis.** `Evil.__eq__` calls `d1.clear()` (frees all blocks) then returns False;
the compare loop's next `deque` cursor step reads a freed block.

**Confidence & dup-check.** Medium. deque mutation has FT critical sections but the
*richcompare iteration* holds block pointers; verify it re-derives / detects length change like
list/heapq do.

---

## Site 5 — `collections._count_elements` (`Counter`) key `__hash__` mutates the mapping

**Site.** `_count_elements` (`Modules/_collectionsmodule.c:2588`) loops
`key = PyIter_Next(it)` then does `mapping[key] = mapping.get(key, 0) + 1` via the C fast path,
holding a borrowed reference to `mapping` and its dict internals across the key's hashing.

**Reasoning.** `key.__hash__`/`__eq__` runs during the get/setitem and can mutate `mapping`
(clear it, or swap it out), invalidating the dict entry the fast path just located.

**Why it fits.** Borrowed dict entry / `mapping` internals held across a hash/eq callback.

**Reachability.** `collections.Counter(iterable_of_evil_keys)` or `Counter().update(...)`.

**Trigger hypothesis.** Colliding evil keys whose `__eq__` clears the Counter during the
`get`→`setitem` window.

**Confidence & dup-check.** Low-medium. The C fast path re-looks-up on setitem; confirm no raw
entry pointer survives the hash. Compare `#142831`-style hardening.

---

## Site 6 — `csv.writer.writerows` borrowed dialect across row `__iter__` / field `__str__`

**Site.** `csv_writerows` (`Modules/_csv.c:1488`) loops `row_obj = PyIter_Next(row_iter)` and
`join_append`s fields, reading `self->dialect->{delimiter,quotechar,lineterminator,escapechar}`
(borrowed `PyObject*`s) throughout.

**Reasoning.** `writer.dialect` is a live attribute; a field's `__str__` or the row iterator's
`__next__` can rebind the writer's dialect, dropping the old `lineterminator`/`quotechar` object
the join loop still reads.

**Why it fits.** Borrowed dialect member objects held across a `__str__`/`__next__` callback that
frees them. (Distinct from the original set's single-`writerow` angle: this is the
`writerows` streaming loop.)

**Reachability.** `w.writerows(EvilRowIter())` where the iterator or a field `__str__` sets
`w.dialect`.

**Trigger hypothesis.** Field `__str__` assigns `w.dialect = other` and drops the old
`lineterminator` last ref before `join_append_data` calls `PyUnicode_FindChar` on it.

**Confidence & dup-check.** Low-medium. Dialect members may be borrowed only transiently;
confirm refcount held across the whole `writerows` loop.

---

## Site 7 — `functools.lru_cache` key `__hash__`/`__eq__` mutates the cache mid-lookup

**Site.** `bounded_lru_cache_get_lock_held` (`Modules/_functoolsmodule.c:1408`) builds the key
(`lru_cache_make_key`, `:1237`), then does a dict lookup and manipulates the borrowed circular
LRU list `self->root` (`lru_list_elem` links) — all while the key's `__hash__`/`__eq__` runs.

**Reasoning.** On the GIL build the per-object critical section is a no-op, so a reentrant call
to the *same* lru-wrapped function (from inside the key's `__hash__`/`__eq__`) mutates
`self->root`/cache dict, freeing the `lru_list_elem` the outer call is about to relink.

**Why it fits.** Borrowed intrusive-list node (`root->prev/next`) held across a hash/eq callback
that frees it via a reentrant cache operation.

**Reachability.** `@lru_cache` a function `f`; call `f(EvilKey())` where `EvilKey.__hash__`
calls `f(...)` again (recursively) to evict/insert.

**Trigger hypothesis.** Reentrant `f` call from `__hash__` fills the cache to `maxsize`, evicting
(freeing) the node the outer `bounded_lru_cache_get_lock_held` then moves to front.

**Confidence & dup-check.** Medium. Concrete re-entry is easy (recursive call). Verify the link
manipulation re-reads `self->root` after `make_key`/lookup rather than caching a node across the
callout.

---

## Site 8 — `dict.__eq__` (`dict_equal`) value compare mutates a compared dict

**Site.** `dict_equal` (`Objects/dictobject.c`) iterates one dict's entries with a raw index and
`PyObject_RichCompareBool(aval, bval, Py_EQ)` on values, holding borrowed `ep`/`ma_values`
pointers into both dicts.

**Reasoning.** A value's `__eq__` can clear/resize either dict, freeing the `ma_keys`/`ma_values`
array `dict_equal` continues to index.

**Why it fits.** Borrowed hash-table arrays held across a value-equality callback that reshapes
the table.

**Reachability.** `d1 == d2` where a shared value object's `__eq__` does `d1.clear()`.

**Trigger hypothesis.** `Evil.__eq__` clears `d1` on the first value compare; `dict_equal`'s next
`ep++`/value fetch reads freed entries.

**Confidence & dup-check.** Medium. `dict_equal` re-fetches via key lookup in `d2` but indexes
`d1` directly; confirm whether it revalidates `d1`'s size/version after each compare.

---

## Site 9 — `_json` C encoder dict path: `default`/key `__str__` mutates the container

**Site.** `encoder_listencode_dict` (`Modules/_json.c`) iterates the object's items (or a
sorted key list) and, for non-serializable values, calls the user `default` callable, while
holding borrowed item/key pointers and the partially built output.

**Reasoning.** `default(obj)` (or a key's `__str__` during coercion) can mutate the dict being
encoded — clearing it or dropping the borrowed value — after the encoder captured the item
pointer. `#142831` fixed the *fast-seq* INCREF; the dict-with-`default` path is less swept.

**Why it fits.** Borrowed container item held across a `default`/`__str__` callback that frees
it.

**Reachability.** `json.dumps(evil_dict, default=cb)` where `cb` mutates `evil_dict`.

**Trigger hypothesis.** `default` pops/clears the dict; the encoder's next borrowed item pointer
is stale.

**Confidence & dup-check.** Low-medium. The encoder often snapshots items into a list first;
confirm the `default`-invocation path doesn't hold a borrowed value across the call.

---

## Site 10 — `range.__contains__` / `.index` `PyObject_RichCompareBool` side effects

**Site.** `range_contains_long` (`Objects/rangeobject.c:459`) and `range_contains`/`range_index`
(`:504`) compare the argument against range bounds/members with `PyObject_RichCompareBool`.

**Reasoning.** For a non-int argument, the slow path runs `arg.__eq__` while holding borrowed
references to the range's `start`/`stop`/`step` PyLongs. Those are owned by the (immutable)
range, so no UAF on the range itself — but if `arg.__eq__` drops the last external ref to a
value the loop later reuses, or re-enters, behavior is worth checking.

**Why it fits.** Comparison callback runs user code inside a C membership loop (shape of the
family), included to bound the family's edge.

**Reachability.** `Evil() in range(10**30)` (bignum path) with `Evil.__eq__` side effects.

**Trigger hypothesis.** `Evil.__eq__` mutates unrelated global state / re-enters; verify the
range members stay valid (expected: yes, range is immutable).

**Confidence & dup-check.** Low (ruling-out). range is immutable so this is almost certainly
safe; documented to close the family's coverage.
</content>

# workflow-0080 — Callback re-entrancy invalidates borrowed state or backing storage

> A native fast path holds unowned references / raw pointers / cached sizes / iterator state
> across a user-defined callback (hash, equality, str/format, iteration, serialization, reduce),
> which re-enters and mutates/clears/frees that state before the operation resumes.

10 fresh sites (distinct from audit7). All single-thread; testable on the GIL ASan/UBSan image
(`@critical_section` is a no-op there). Sites 2, 5, 7, 10 are the open leads; the rest identify
their guard inline.

---

## Site 1 — `array.array` richcompare (`array_richcompare`) borrowed `ob_item` across element `__eq__`

**Site.** `array_richcompare` (`Modules/arraymodule.c:864`) compares two arrays element-wise via
`PyObject_RichCompareBool` while indexing both arrays' `ob_item` buffers.

**Reasoning.** For object-typecode arrays, an element `__eq__` can `frombytes`/`del a[:]` on
either operand, reallocating `ob_item`; a cached base pointer or stale length would fault.

**Why it fits.** Borrowed typed-buffer storage held across an equality callback that reallocs it.

**Reachability.** `array('O',[Evil()]) == array('O',[x])` (object array) where `Evil.__eq__`
resizes an operand. (Note: numeric-typecode arrays don't run Python per element.)

**Trigger hypothesis.** `Evil.__eq__` shrinks one array; the compare loop reads past the new end.

**Confidence & dup-check.** **Low-medium.** Object-typecode arrays are the only path that runs
Python per element and are less exercised than numeric ones. Verify `array_richcompare` re-reads
`Py_SIZE`/re-derives `ob_item` each step like `array_array_index_impl` does (`:1342`). `git log
--grep "array_richcompare"`.

---

## Site 2 — `set.difference_update` / `symmetric_difference_update` element `__hash__` reshapes the set  ⭐

**Site.** `set_difference_update_internal` / `set_symmetric_difference_update`
(`Objects/setobject.c`) iterate the other operand computing `PyObject_Hash(key)` and probing
`so->table` with a raw `setentry *entry`, and (for symmetric-difference) also insert.

**Reasoning.** `key.__hash__`/`__eq__` runs Python and can `so.clear()` / add elements,
triggering `set_table_resize` that frees the `table`/`entry` the surrounding probe still holds.

**Why it fits.** Borrowed hash-table `entry`/`table` pointer held across a `__hash__` callback
that reshapes the same set — the `#143546` (in-place set intersection) mechanism on the
*difference* variants (audit7 covered `update`/`intersection`).

**Reachability.** `so.difference_update(EvilIter())` / `so ^= EvilIter()` where elements'
`__hash__` mutate `so`.

**Trigger hypothesis.** `Evil.__hash__` calls `so.clear()` (frees table) then returns a constant;
the next `set_add_entry`/`set_discard_entry` uses the freed table.

**Confidence & dup-check.** **Medium.** `set` add/discard use a `restart:` re-read of `so->table`
in the hardened paths — verify the *difference*-family loops re-read `so->table` after each
`__hash__`, not just the add path. `git log --grep "set.*reentr\|set_table_resize"` /
`gh search issues "set difference_update use-after-free"`.

---

## Site 3 — `dict.update` / `dict_merge` from a non-dict mapping: `keys()`/`__getitem__` mutate the destination

**Site.** `dict_merge` (`Objects/dictobject.c`) for a mapping without the dict fast path calls
`mapping.keys()` then, per key, `mapping[key]` and inserts into the destination — running user
`keys()`/`__getitem__`/`__hash__` while holding borrowed destination `ma_keys`.

**Reasoning.** The source mapping's Python methods can mutate the *destination* dict (or the key
list), invalidating the `ma_keys`/insertion position the merge loop assumes.

**Why it fits.** Borrowed container backing held across a mapping-protocol callback (`#140551`
hash/eq-clears-mapping-during-insert shape).

**Reachability.** `d.update(EvilMapping())` where `EvilMapping.__getitem__` does `d.clear()`.

**Trigger hypothesis.** `__getitem__` clears the destination mid-merge; the next
`insertdict`/`ma_keys` access is stale.

**Confidence & dup-check.** **Low-medium (ruling-out).** `insertdict` re-derives `ma_keys` and
handles resize, so the destination is likely safe; the sharp part is the borrowed *key list* from
`keys()`. Verify the merge snapshots keys (it may materialize a list). `git log --grep
"dict_merge\|PyDict_Merge"`.

---

## Site 4 — `tuple.index` / `.count` / `__contains__` element `__eq__` side effects

**Site.** `tuplecontains` / `tupleindex` / `tuplecount` (`Objects/tupleobject.c`) loop
`PyObject_RichCompareBool(self->ob_item[i], v, Py_EQ)`.

**Reasoning.** Included to bound the family: a compared value's `__eq__` runs Python inside a C
membership loop over borrowed `ob_item`.

**Why it fits.** Comparison callback inside a C search loop over borrowed container storage.

**Reachability.** `Evil() in (a, b, c)` with side-effecting `Evil.__eq__`.

**Trigger hypothesis.** `Evil.__eq__` mutates unrelated state / re-enters; the tuple's own
storage is checked for stale reads.

**Confidence & dup-check.** **Very low (ruling-out).** Tuples are immutable — `ob_item` cannot be
resized/freed while the tuple is alive (pinned by the call), so no UAF on the container. Kept only
to document the immutable boundary of the family; cross off.

---

## Site 5 — `str.__mod__` / `str.format` field `__format__`/`__str__` mutates the args container  ⭐

**Site.** `unicode_format` / `do_string_format` / `PyUnicode_Format` (`Objects/unicodeobject.c`)
walk a borrowed args tuple or a `{}`-field mapping, calling each field's `__format__`/`__str__`/
`__repr__` while holding borrowed field/arg pointers and the growing `_PyUnicodeWriter` result.

**Reasoning.** A field's `__format__`/`__str__` is arbitrary Python and can mutate the args
sequence/mapping (clear/replace it), freeing a borrowed field object the formatter reads next —
the `bytearray`-format UAF `#142557` mechanism transposed onto `str` formatting.

**Why it fits.** Borrowed argument-container entries held across a formatting callback that frees
them.

**Reachability.** `"{0}{1}".format(Evil(), x)` where `Evil.__format__` mutates the arg tuple, or
`"%s%s" % (Evil(), x)` where `Evil.__str__` clears a shared args list.

**Trigger hypothesis.** `Evil.__format__` drops the last ref to the next positional arg (e.g. via
clearing a list passed with `*args`); the formatter's next borrowed field is stale.

**Confidence & dup-check.** **Low-medium (open).** `%`-formatting takes a tuple (immutable) for
the common case, so the sharp path is `format(*evil_list)` / a mapping-based `format_map` whose
`__getitem__`/field callback mutates the mapping. Verify the formatter re-looks-up mapping fields
vs. caching. `git log --grep "unicode.*format.*reentr"`; compare `#142557` (bytearray variant,
fixed).

---

## Site 6 — `list.sort` custom `key` / `__lt__` mutates the list during the sort

**Site.** `list_sort_impl` (`Objects/listobject.c`) computes keys and runs the merge, calling the
`key` function and element `__lt__` (arbitrary Python) during ordering.

**Reasoning.** A `key`/`__lt__` that mutates the list mid-sort could invalidate the working
storage.

**Why it fits.** Comparison/key callback re-entrancy during an in-place C operation over the
list's storage.

**Reachability.** `l.sort(key=Evil)` / list of objects with side-effecting `__lt__` that clears
`l`.

**Trigger hypothesis.** `key`/`__lt__` clears `l`; the sort continues over swapped-out storage.

**Confidence & dup-check.** **Very low (ruling-out).** Verified hardened by design: `list.sort`
swaps `ob_item` out to an empty list for the duration and restores it, and detects "list modified
during sort" → `ValueError`. Longstanding guard. Cross off.

---

## Site 7 — `_pickle` `batch_appends` / `batch_setitems` recursive `save` runs `__reduce__` mid-batch  ⭐

**Site.** `batch_appends` / `batch_setitems` (`Modules/_pickle.c`) iterate a container in chunks,
calling `save()` on each element/key/value; `save` recursively dispatches `__reduce_ex__`/
`__reduce__`/`persistent_id` (arbitrary Python) while the batch loop holds borrowed iterator
state and pointers into the shared `Pickler` framing/memo buffers.

**Reasoning.** A reduced object's `__reduce__` can mutate the container being pickled (append/
clear) or the `Pickler`'s buffers; a borrowed batch pointer or cached count used after `save`
returns can be stale — the dump-side analogue of the load-side reentrancy (`#143639`).

**Why it fits.** Borrowed serializer/iteration state held across a `__reduce__`/`persistent_id`
callback that mutates the same operation.

**Reachability.** `pickle.dumps(container)` where an element's `__reduce__` clears/extends
`container` or re-enters `pickler.dump`.

**Trigger hypothesis.** During `batch_appends`, element `k`'s `__reduce__` clears the list;
the loop's cached length/iterator reads freed storage.

**Confidence & dup-check.** **Low-medium (open).** audit5 found the *load* side re-derives
`self->stack->data` after callouts; the *dump* batch side is separately audited. Verify the batch
loop re-reads the iterator/`Pickler` buffers after each `save`. `git log --grep
"batch_appends\|save_reduce"`; distinct from `#143638` (pickle load state mutation).

---

## Site 8 — `memoryview` richcompare (`memory_richcompare`) element unpack releases a view

**Site.** `memory_richcompare` (`Objects/memoryobject.c`) compares two memoryviews element-wise,
unpacking items and comparing while holding both `self->view.buf` pointers.

**Reasoning.** For object/format views the per-element unpack/compare can run Python that
`release()`s a view or resizes its exporter, freeing the buffer later iterations read.

**Why it fits.** Borrowed exported buffer held across an element comparison callback.

**Reachability.** `mv1 == mv2` where an element compare releases `mv1`.

**Confidence & dup-check.** **DUP-risk — do not re-file without checking.** This is the mechanism
of `#142663` ("element unpacking during memory comparison could release a view and resize its
exporter"), listed in the workflow-0080 evidence. Verify whether `#142663`'s fix covers
`memory_richcompare` specifically or only the search path; only a genuinely uncovered method is
reportable.

---

## Site 9 — `functools.cmp_to_key` comparator re-entrancy during `sorted`/`list.sort`

**Site.** `keyobject_richcompare` (`Modules/_functoolsmodule.c`) calls the user `cmp(a, b)` on the
borrowed wrapped objects `ko->object` when the sort compares two `K` keys.

**Reasoning.** The `cmp` callable is arbitrary Python; invoked during a sort it can mutate the
sequence being sorted or drop refs to other key wrappers, but each `keyobject` holds its own ref
to `ko->object`.

**Why it fits.** User comparator callback runs inside the sort's compare over borrowed key
wrappers.

**Reachability.** `sorted(objs, key=functools.cmp_to_key(evil_cmp))` where `evil_cmp` mutates
`objs`.

**Trigger hypothesis.** `evil_cmp` clears the source list; the sort's swapped-out storage handles
it, but verify the `keyobject`s stay valid.

**Confidence & dup-check.** **Low (ruling-out).** `list.sort` protects its storage (Site 6) and
each `keyobject` owns `ko->object`; likely safe. Kept as a comparator-reentrancy lead. `git log
--grep "cmp_to_key"`.

---

## Site 10 — `_json` C encoder list path (`encoder_listencode_list`) borrowed item across `__iter__`/`default`  ⭐

**Site.** `encoder_listencode_list` (`Modules/_json.c`) iterates a list/sequence, and for
non-serializable elements calls the user `default` callable, while holding borrowed item pointers
and the partially-built `_PyUnicodeWriter` output.

**Reasoning.** `default(obj)` (or a subclass's `__iter__`/`__len__`) can mutate the list being
encoded — clearing it or dropping the borrowed element — after the encoder captured the item
pointer. `#142831` hardened the *fast-seq INCREF*; the list-with-`default` recursion is
less-swept.

**Why it fits.** Borrowed container item held across a `default`/iteration callback that frees it.

**Reachability.** `json.dumps(evil_list, default=cb)` where `cb` mutates `evil_list`.

**Trigger hypothesis.** `default` pops/clears the list mid-encode; the encoder's next borrowed
item pointer is stale.

**Confidence & dup-check.** **Low-medium (open).** audit7 examined the *dict* path; the *list*
path (`encoder_listencode_list`) is distinct. Verify it re-reads / INCREFs the element around the
`default` callout like the fast-seq path. `git log --grep "listencode\|_json.*INCREF"`; compare
`#142831`.
</content>

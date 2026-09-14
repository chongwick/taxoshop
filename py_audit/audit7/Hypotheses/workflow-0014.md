# workflow-0014 — Borrowed/derived handle used after owner or backing storage is invalidated

> A non-owning pointer, derived view, cache slot, iterator cursor, or cross-owner reference
> survives an operation that invalidates its target (release/close, resize, mutation, teardown,
> error-path decref) and is then used as if still valid.

10 fresh sites. Single-thread ones are testable on the GIL ASan/UBSan image.

---

## Site 1 — `memoryview.index` / `.count` use view after reentrant `release()`  ⭐

**Site.** `memoryview_index_impl` (`Objects/memoryobject.c:2984`) and the count loop
(`:2904`) call `memory_item(obj, index)` each iteration and then
`PyObject_RichCompareBool(item, value, Py_EQ)`. A source comment asserts *"memoryviews can be
mutated during iterations … their shape cannot"* and treats the index as valid for the whole
loop. `CHECK_RELEASED` is checked only once, at entry.

**Reasoning.** `value.__eq__` is arbitrary Python run mid-loop. If it calls `mv.release()`
(or drops the last ref to a memoryview that then releases), `self->view` is torn down, but the
loop keeps calling `memory_item` on the released view → dereference of a freed/NULL buffer.

**Why it fits.** Derived view (`self->view.buf`) held across a user callback that invalidates
the backing buffer; the loop's "index still valid" assumption is broken by release.

**Reachability.** `memoryview(bytearray(b"abc..")).index(Evil())` where `Evil.__eq__` calls the
view's `.release()`. No ctypes.

**Trigger hypothesis.** `Evil.__eq__` grabs the memoryview (module global) and calls
`mv.release()` on the first compare, then returns False; the next `memory_item` reads a released
view.

**Confidence & dup-check.** Medium. The explicit "shape cannot change" comment only reasons
about shape, not release — likely an overlooked case. Confirm `memory_item` re-checks
`CHECK_RELEASED`; grep `gh search issues "memoryview index release"`.

---

## Site 2 — `functools.partial.__call__` borrowed `pto->fn` across the wrapped call

**Site.** `partial_call` (`Modules/_functoolsmodule.c:592`) reads `pto->fn`, `pto->args`,
`pto->kw` (all borrowed from the partial object) and builds the merged arg vector, then calls
`fn`. Argument merging and the call run user code (arg `__index__`/keyword hashing, `fn` itself).

**Reasoning.** If the partial object is only referenced from a place the callee can clear (e.g.
`fn` deletes the attribute/global holding the partial, or a weakref callback fires), `pto->fn`
and `pto->args` can be freed while `partial_call` still holds the borrowed pointers for the
post-call cleanup / vectorcall temp.

**Why it fits.** Borrowed owner fields used across a callout that can drop the owner's last ref.

**Reachability.** `p = functools.partial(f, evil); del_the_only_ref_to_p_inside_f(); p()`.

**Trigger hypothesis.** `f` does `globals().pop('p')` (last ref) so the partial is freed during
the call, then the epilogue touches `pto->args`.

**Confidence & dup-check.** Low-medium. `partial_call` likely holds an owned ref to `pto` for
the call duration (tp_call keeps `self` alive). Ruling-out lead; verify no borrowed field is
used after a step that can run user code without an owning ref.

---

## Site 3 — `os.scandir` `DirEntry` methods use borrowed path/fd after iterator close

**Site.** `ScandirIterator` holds an open directory handle/`dirfd`; `DirEntry.stat()`,
`.is_dir()`, `.is_file()` (posixmodule `DirEntry_*`) resolve relative to the iterator's
`path`/`dirfd`. Closing the iterator (`scandir().close()` / exhaustion / GC) frees that context.

**Reasoning.** A retained `DirEntry` whose owning `ScandirIterator` was closed can call
`stat(follow_symlinks=False)` which uses the now-closed `dirfd` (or freed path buffer).

**Why it fits.** Derived object outlives the backing OS resource of its owner.

**Reachability.** `it = os.scandir("."); e = next(it); it.close(); e.stat()`. No ctypes.

**Trigger hypothesis.** Close the iterator (freeing/closing `dirfd`), then call `e.stat()` /
`e.is_dir()` → operate on a closed fd or freed path.

**Confidence & dup-check.** Low-medium. DirEntry caches lstat results and may store its own
path copy; confirm whether `stat()` re-opens vs. reuses the iterator's `dirfd`.

---

## Site 4 — `dict_items` / `dict_keys` view comparison borrows `dv_dict` across element `__eq__`

**Site.** `dictview_richcompare` → `all_contained_in` (`Objects/dictobject.c`) iterates one view
while doing membership tests whose element `__eq__`/`__hash__` runs Python, holding the borrowed
`dv->dv_dict` and its `ma_keys` across the callout.

**Reasoning.** A key/value object with a side-effecting `__eq__` can clear the dict backing one
view mid-comparison, freeing `ma_keys`/entries that the traversal continues to read.

**Why it fits.** Borrowed container backing (`ma_keys`) held across a comparison callback that
frees it — the OrderedDict #142637 mechanism transposed onto plain-dict views.

**Reachability.** `d1.items() == d2.items()` where a key's `__eq__` does `d1.clear()`.

**Trigger hypothesis.** Colliding-hash keys force `__eq__`; that `__eq__` clears the other dict
whose view is being traversed → stale entry read.

**Confidence & dup-check.** Medium. Plain-dict lookups are broadly hardened, but the *view*
compare path re-derives less. Verify `all_contained_in` re-reads the dict each step.

---

## Site 5 — `sqlite3.Row.__getitem__(name)` borrows `Cursor.description` across name compare

**Site.** `pysqlite_row_subscript` (`Modules/_sqlite/row.c`) for a string key walks
`self->description` (borrowed from the originating cursor), comparing column names via
`PyUnicode`/`PyObject_RichCompareBool`.

**Reasoning.** `Row` keeps a reference to the cursor's description; if the key is a `str`
subclass whose `__eq__` closes the connection / resets the cursor (freeing `description`), the
loop reads freed tuple storage.

**Why it fits.** Cross-owner borrowed metadata (`description`) used after the owner (cursor)
invalidates it.

**Reachability.** `row[EvilName("col")]` where `EvilName.__eq__` calls `con.close()`.

**Trigger hypothesis.** `EvilName.__eq__` resets/closes the cursor mid-scan; the next name
comparison dereferences a freed `description` element.

**Confidence & dup-check.** Low-medium. `Row` likely holds its own ref to `description`
(keeping it alive). Confirm whether closing the cursor clears the description the row borrows.

---

## Site 6 — `contextvars.Token.reset` uses borrowed `old_value` after context churn

**Site.** `Python/context.c` `contextvar_reset` restores `tok->tok_oldval` (borrowed at token
creation) into the current context; between `set()` and `reset()`, `old_value` may have been the
only strong ref elsewhere.

**Reasoning.** If intervening `Context` operations (copy/run/enter that replace the context) drop
the last reference to the old value, the token's borrowed `tok_oldval` dangles when `reset()`
writes it back.

**Why it fits.** A saved handle (`tok_oldval`) used after intervening operations invalidate it.

**Reachability.** `tok = cv.set(x); ...churn contexts, drop x...; cv.reset(tok)`.

**Trigger hypothesis.** Between set and reset, run code that removes the var and drops `x`'s last
ref; reset re-publishes a freed value.

**Confidence & dup-check.** Low. Token almost certainly owns `tok_oldval`. Ruling-out lead;
confirm the token holds a strong ref.

---

## Site 7 — `type.__new__` `__set_name__` loop over a borrowed namespace

**Site.** During class creation, `type_new_set_names` / `set_names` (`Objects/typeobject.c`)
iterate the new type's `tp_dict` calling each descriptor's `__set_name__(owner, name)`, holding
borrowed references into the dict being iterated.

**Reasoning.** A descriptor's `__set_name__` can mutate the owner class's `__dict__`
(add/delete attributes), reshaping the mapping the loop is walking → stale entry / freed value.

**Why it fits.** Borrowed container (class dict) entries used across a user hook that mutates it.

**Reachability.** Define a class with a descriptor whose `__set_name__` does
`delattr(owner, other_attr)` / `type.__setattr__` on the owner.

**Trigger hypothesis.** `__set_name__` deletes a sibling descriptor from the class dict during
the set-names pass → the loop reads a freed entry.

**Confidence & dup-check.** Medium. Confirm whether `set_names` snapshots the items into a tuple
first (it may). `git log --grep "__set_name__"`.

---

## Site 8 — generator/coroutine `gi_frame` used after `close()`/`throw()` finalizer

**Site.** `gen_send_ex2` / `gen_close` (`Objects/genobject.c`) hold a borrowed `gen->gi_frame`
(`_PyInterpreterFrame`) across running the frame, whose finalization (GeneratorExit handling,
`finally` blocks) can run user code.

**Reasoning.** If a `finally`/`__del__` reached during `close()` resurrects or re-enters the
generator (or drops the generator's last external ref), the borrowed frame pointer used after the
callout may reference torn-down frame state.

**Why it fits.** Borrowed execution-state handle used after a finalizer callout invalidates it.

**Reachability.** A generator whose `finally` block calls `gen.throw()`/re-enters, driven by
`gen.close()`.

**Trigger hypothesis.** `close()` triggers `GeneratorExit`; the `finally` re-enters the same
generator, confusing `gi_frame_state` and leaving the outer close using a stale frame.

**Confidence & dup-check.** Low-medium. Generator reentrancy is guarded (`gi_frame_state` /
"already executing"). Verify the state machine covers close-time re-entry.

---

## Site 9 — `super.__getattribute__` borrows `__mro__` across a descriptor `__get__`

**Site.** `super_getattro` (`Objects/typeobject.c`) walks `su_obj_type->tp_mro` (borrowed tuple)
and, on a hit, calls the found descriptor's `__get__`, which is user code, while the borrowed
`mro` pointer/index is live.

**Reasoning.** A descriptor `__get__` that reassigns the instance's/type's `__class__` or
`__bases__` triggers MRO recomputation, freeing the borrowed `tp_mro` tuple the loop still holds.

**Why it fits.** Borrowed type-metadata (`tp_mro`) used after a callback invalidates it
(sibling of the `#108253` version-cache mechanism, single-thread variant).

**Reachability.** `super().attr` where `attr` resolves to a data descriptor whose `__get__`
sets `type(self).__bases__ = (...)`.

**Trigger hypothesis.** `__get__` mutates `__bases__` (frees old `tp_mro`); `super_getattro`
continues reading the freed mro tuple.

**Confidence & dup-check.** Medium. Confirm `super_getattro` INCREFs the mro tuple for the walk
(it may hold `su_obj_type` but not pin `tp_mro`).

---

## Site 10 — `_io.BufferedRWPair` borrowed reader/writer across a callout

**Site.** `bufferedrwpair` (`Modules/_io/bufferedio.c`) forwards to `self->reader` /
`self->writer` (borrowed sub-objects) across methods that can run Python (a raw layer whose
`readable()`/`writable()`/`readinto` is a Python object).

**Reasoning.** A raw stream method invoked through the pair can drop the pair's last ref or
reassign `reader`/`writer`, freeing the sub-object the pair method continues to use — the
`TextIOWrapper.detach` (audit4) / `#154997` mechanism on the less-swept RWPair.

**Why it fits.** Borrowed composed sub-object used after a reentrant callout frees it.

**Reachability.** `BufferedRWPair(EvilRaw(), EvilRaw())` where a raw method detaches/clears the
pair.

**Trigger hypothesis.** `EvilRaw.readinto` drops the pair's last external ref (or a wrapper
detaches the reader) mid-`read` → borrowed `self->reader` dangles.

**Confidence & dup-check.** Low-medium. RWPair is far less swept than Buffered{Reader,Writer};
compare to `#154997`. Confirm whether pair methods hold owned refs to reader/writer.
</content>

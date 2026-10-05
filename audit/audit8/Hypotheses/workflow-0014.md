# workflow-0014 — Borrowed/derived handle used after owner or backing storage is invalidated

> A non-owning pointer, derived view, cache slot, iterator cursor, borrowed field, or
> cross-owner reference survives an operation that invalidates its target (release/close,
> resize, mutation, teardown, error-path decref) and is then used as though still valid.

10 fresh sites (distinct from audit7). Single-thread ones are testable on the GIL ASan/UBSan
image. Sites 4, 5, 8, 10 are the genuinely-open leads; 1–3, 6–7, 9 are ruling-out leads whose
guard is identified inline.

---

## Site 1 — `array.array.index` / `.count` / `.remove` borrowed `ob_item` across `__eq__`

**Site.** `array_array_index_impl` (`Modules/arraymodule.c:1342`), `array_array_count_impl`
(`:1304`), `array_array_remove_impl` (`:1402`) loop calling
`PyObject_RichCompareBool(getarrayitem(self,i), v, Py_EQ)` over the array's `ob_item` buffer.

**Reasoning.** `v.__eq__` runs arbitrary Python each iteration and can `arr.frombytes(...)` /
`del arr[:]`, which `PyMem_Realloc`s or frees `ob_item`; a loop that cached the raw pointer
would dereference freed storage.

**Why it fits.** Derived buffer (`ob_item`) held across an equality callback that reallocs it.

**Reachability.** `array('b', b'abc').index(Evil())` where `Evil.__eq__` resizes the array.

**Trigger hypothesis.** `Evil.__eq__` shrinks/grows the array on the first compare; the next
element read touches moved/freed storage.

**Confidence & dup-check.** **Low (ruling-out).** Verified guarded: the loop condition re-reads
`i < Py_SIZE(self)` every iteration and `getarrayitem` re-derives `ob_item` from `self` and
bounds-checks — a source comment ("Use Py_SIZE() for every iteration in case the array is
mutated during PyObject_RichCompareBool()") documents the fix. `git log --grep "array.*index"`
shows no open reentrancy issue. Cross off unless a variant path (`__contains__` at `:1377`)
caches differently.

---

## Site 2 — `collections.deque.index` / `.count` / `.remove` / `__contains__` block cursor across `__eq__`

**Site.** `deque_count_impl` (`Modules/_collectionsmodule.c:1159`), `deque_index_impl` (`:1262`),
`deque_remove_impl` (`:1461`), `deque_contains_lock_held` (`~:1196`) walk the intrusive
`block *b` linked list holding `b->data[index]` while calling `PyObject_RichCompareBool`.

**Reasoning.** An element's `__eq__` can `d.clear()`/`d.append()` which frees or relinks the
`block` the cursor points into; continuing to walk `b->rightlink` would traverse freed blocks.

**Why it fits.** Borrowed block-list cursor held across an equality callback that frees blocks —
the OrderedDict #142637 mechanism transposed onto deque search methods (audit7 covered
`deque_richcompare`, not these).

**Reachability.** `d.index(Evil())` / `Evil() in d` where `Evil.__eq__` does `d.clear()`.

**Trigger hypothesis.** `__eq__` clears the deque on the first compare; the loop's block advance
reads a freed block.

**Confidence & dup-check.** **Low (ruling-out).** Verified guarded: each of these captures
`start_state = deque->state` and, after every compare, checks `start_state != deque->state` →
`RuntimeError("deque mutated during iteration")` *before* advancing the cursor. `git log --grep
"deque.*mutat"` — the guard predates HEAD. Verify `deque_remove` (which also deletes) re-reads
`state` after the compare that precedes its `_deque_delitem`.

---

## Site 3 — `list.__eq__`/`__lt__` (`list_richcompare_impl`) borrowed `ob_item[i]` across element compare

**Site.** `list_richcompare_impl` (`Objects/listobject.c:3438`) loops
`for (i=0; i<Py_SIZE(vl) && i<Py_SIZE(wl); i++)` reading `vl->ob_item[i]`/`wl->ob_item[i]` then
`PyObject_RichCompareBool(vitem, witem, Py_EQ)`.

**Reasoning.** An element's `__eq__` can `list.clear()`/`del l[:]`/`l.append()` on either
operand, reallocating or freeing `ob_item`; a stale cached `ob_item` base or a stale length
would produce an OOB/UAF read.

**Why it fits.** Borrowed container-element storage held across an equality callback that
resizes it (`#120298` list-compare-frees-element mechanism).

**Reachability.** `[Evil()] == [x]` where `Evil.__eq__` mutates one of the lists.

**Trigger hypothesis.** `Evil.__eq__` clears `vl`; the next iteration indexes freed `ob_item`.

**Confidence & dup-check.** **Low (ruling-out).** Verified guarded: the loop re-evaluates
`Py_SIZE(vl)`/`Py_SIZE(wl)` in the condition and re-derives `vl->ob_item[i]` each iteration, and
`Py_INCREF`s both items before the callout (documented: "may release the GIL and allow the list
to be mutated"). This is the fixed sibling of `#120298`. Cross off; kept to close the family.

---

## Site 4 — `_asyncio` `future_schedule_callbacks` borrowed `fut->fut_loop` across `call_soon`  ⭐

**Site.** `future_schedule_callbacks` (`Modules/_asynciomodule.c:423`) iterates the callbacks
list calling `call_soon(state, fut->fut_loop, cb, (PyObject*)fut, ctx)` (`:479`). The
`fut_callbacks` list is defensively detached (`callbacks = fut->fut_callbacks; fut->fut_callbacks
= NULL;` at `:471`) with an explicit "evil call_soon could change fut->fut_callbacks" comment —
but `fut->fut_loop` is **re-read borrowed** on every `call_soon` and is *not* pinned across the
loop.

**Reasoning.** `call_soon` invokes `loop.call_soon(...)` — arbitrary Python. A callback (or a
`__getattr__`/property on a custom loop) can rebind `fut._loop = None` / reassign the future's
loop, dropping the last ref to the original loop object; the next iteration's
`call_soon(..., fut->fut_loop, ...)` then reads a freed loop pointer.

**Why it fits.** The list is protected by ownership transfer, but a *second* borrowed field
(`fut_loop`) read across the same callout is not — a classic "guarded the obvious handle, missed
the adjacent one" 0014 shape.

**Reachability.** A `Future` with ≥2 callbacks whose first callback sets `fut._loop` to a fresh
object and drops the original loop's last reference, then completes the future.

**Trigger hypothesis.** First `call_soon` runs a callback that reassigns/clears `fut_loop`; the
second iteration passes the freed `fut_loop` to `call_soon` → UAF read of the loop object.

**Confidence & dup-check.** **Medium (open).** The list guard shows the authors reasoned about
`fut_callbacks`/`callback0` but the comment does not mention `fut_loop`. Confirm whether
`fut_loop` can be rebound while a future is scheduling (the C `Future.__init__` stores it; check
for a setter / `__dict__` exposure). `git log --grep "fut_loop"` / `gh search issues
"asyncio Future _loop"`. Note the pure-Python impl is default; ensure `_asyncio` C accel is
active.

---

## Site 5 — `itertools.tee` / `_tee_dataobject` shared borrowed link across a sibling consumer  ⭐

**Site.** The `tee` object and its backing `teedataobject` (`Modules/itertoolsmodule.c`, `tee`/
`teedataobject_getitem`/`teedataobject_jumplink`) share a linked chain of value buffers; each
`tee` iterator holds a borrowed `dataobj`/`index` cursor into the shared chain and pulls from the
common source iterator on demand.

**Reasoning.** Advancing one `tee` branch runs the source iterator's `__next__` (arbitrary
Python) and appends to / links new `teedataobject` nodes; if that user code drops the last
reference to a sibling branch or to an already-consumed node, a branch holding a borrowed
`dataobj` pointer can read a freed node when it next resumes.

**Why it fits.** Derived shared-state cursor (`dataobj`, `index`) held across a callback that can
free the backing node — a cross-owner lifetime failure (`#146011` derived-view shape).

**Reachability.** `a, b = itertools.tee(EvilSource()); next(a)` where `EvilSource.__next__`
manipulates references to `b` / the tee chain, then `next(b)`.

**Trigger hypothesis.** The source `__next__` (invoked while branch A advances) drops branch B's
node ref; B's subsequent `teedataobject_getitem` reads the freed node.

**Confidence & dup-check.** **Low-medium (open).** tee refcounts nodes, so plain use is safe; the
sharp case is a source `__next__` that reaches into the tee internals. Distinct from the
free-threaded #123471 sprint (this is the *single-thread lifetime* axis). Verify
`teedataobject_getitem` holds a strong ref to the node across the `__next__` callout;
`git log --grep "teedataobject"`.

---

## Site 6 — `weakref.proxy` binary/in-place operators dereference `_PyWeakref_GET_REF` referent

**Site.** The proxy `WRAP_BINARY`/`WRAP_TERNARY`/`WRAP_INPLACE` macros
(`Objects/weakrefobject.c:607`, `proxy_call` `:609`, `proxy_repr` `:612`, `proxy_setattr`
`:632`, etc.) each do `PyObject *obj = _PyWeakref_GET_REF(proxy);` then operate on `obj`.

**Reasoning.** A proxied object could be collected mid-operation if only weakly held; using a
borrowed referent after it is cleared would be a UAF.

**Why it fits.** Cross-owner borrowed reference (the weak referent) used during an operation that
can run user code (`obj.__op__`).

**Reachability.** `p = weakref.proxy(obj)` then an operation whose callee drops `obj`'s last
strong ref.

**Trigger hypothesis.** `p + Evil()` where `Evil.__radd__` drops `obj`'s last strong ref, then
the proxy continues using the referent.

**Confidence & dup-check.** **Low (ruling-out).** Verified guarded: modern proxy code uses
`_PyWeakref_GET_REF` which returns a **new strong ref** (the pattern replaced the old borrowed
`PyWeakref_GET_OBJECT`), and each WRAP macro `Py_DECREF(obj)` after the call. The referent is
pinned for the operation. `git log --grep "_PyWeakref_GET_REF"` confirms the hardening. Cross off
unless a hand-written proxy method still uses the borrowed accessor.

---

## Site 7 — `csv.reader` (`Reader_iternext`) borrowed `self->dialect` across the input iterator `__next__`

**Site.** `Reader_iternext` (`Modules/_csv.c`) calls `PyIter_Next(self->input_iter)` to fetch
each source line while holding borrowed `self->dialect` (and its `delimiter`/`quotechar`/
`escapechar` member objects) and the partially-built `self->fields` list.

**Reasoning.** The input iterator's `__next__` is arbitrary Python and can rebind
`reader.dialect`-adjacent state or reach into the reader; a borrowed dialect member freed by that
callout would be read by `parse_process_char` on the returned line.

**Why it fits.** Borrowed configuration objects held across a per-line `__next__` callback that
can invalidate them.

**Reachability.** `csv.reader(EvilLineIter())` where `EvilLineIter.__next__` mutates the reader
or drops the last ref to a dialect member.

**Trigger hypothesis.** `__next__` swaps out the dialect (dropping the old `quotechar`'s last
ref) before returning a line that the parser then quotes.

**Confidence & dup-check.** **Low (ruling-out).** `Dialect` is largely immutable once built and
the reader holds a ref to it; the exposure is only if a member object can be freed while the
`Dialect` still points at it. Verify `Reader_iternext` re-reads `self->dialect` after
`PyIter_Next`. `git log --grep "_csv.*reentr"` — none. Related audit7 site was `csv.writerows`
(distinct method).

---

## Site 8 — `mappingproxy` comparison/containment borrows the wrapped mapping across element `__eq__`  ⭐

**Site.** `mappingproxy` methods (`Objects/descrobject.c`, `mappingproxy_richcompare` /
`mappingproxy_contains` / `mappingproxy_get`) forward to the borrowed `pp->mapping` (e.g.
`PyObject_RichCompare(pp->mapping, other, op)`, `PyDict_Contains(pp->mapping, key)`).

**Reasoning.** A `mappingproxy` typically wraps a type's `tp_dict` or a user dict; the comparison
runs element `__eq__`/`__hash__` which can, via the owning type or an alias, clear or replace the
underlying mapping, freeing storage the forwarded operation still traverses.

**Why it fits.** Borrowed backing container held across a comparison/containment callback that can
invalidate it (`#114106` mutated-mapping-cached-data shape).

**Reachability.** `type(C).__dict__ == other` or `key in cls.__dict__` where `key.__hash__`/
`other`'s `__eq__` triggers `C.__dict__`-mutating type surgery (`del C.attr` / reassigning
`__bases__`).

**Trigger hypothesis.** `key.__hash__` mutates the class dict during `mappingproxy_contains`,
freeing entries the underlying `PyDict_Contains` probe reads.

**Confidence & dup-check.** **Low-medium (open).** The wrapped dict is refcounted (proxy holds a
ref to the *dict object*), but a `dict.clear()` frees `ma_keys` while keeping the object alive —
the exposure is whether the forwarded C call re-reads `ma_keys` after the callout (plain dict is
broadly hardened, but the proxy-forwarded path is less swept). Verify `pp->mapping` operations go
through hardened `dict` internals. `git log --grep "mappingproxy"`.

---

## Site 9 — `_asyncio.Task` `task_step` / `task_wakeup` borrowed `task_fut_waiter` / `task_coro`

**Site.** `task_step_impl` / `task_wakeup` (`Modules/_asynciomodule.c`) read borrowed
`task->task_fut_waiter` and `task->task_coro` across the coroutine `send`/`throw` and the result
inspection (`_asyncio_future_blocking` handling, `future_add_done_callback`).

**Reasoning.** Driving the coroutine runs arbitrary Python (`gen.send`), which can cancel the
task, reassign `task._coro`/`task._fut_waiter`, or drop the last external ref to the awaited
future; a borrowed field used after the `send` returns would dangle.

**Why it fits.** Borrowed execution-state fields held across a user-code callout that can replace
or free them (`#148382` callback-replaces-context shape).

**Reachability.** A coroutine whose awaited object's `__await__`/`send` reaches back and reassigns
the running task's `_coro`/`_fut_waiter`.

**Trigger hypothesis.** During `task_step`, the coroutine's `send` triggers code that clears
`task->task_fut_waiter`'s last ref; the epilogue reads the freed waiter.

**Confidence & dup-check.** **Low (ruling-out-ish).** asyncio's C accel is heavily hardened and
uses `Py_XSETREF`/owned refs across `send`. Confirm each borrowed field is re-fetched or pinned
after `send`/`throw`. `git log --grep "task_step\|fut_waiter"` / `gh search issues "asyncio Task
step use-after-free"`.

---

## Site 10 — `_json` scanner `_parse_object_unicode` borrowed `rval`/pairs across `object_pairs_hook` / key `memo`  ⭐

**Site.** `_parse_object_unicode` (`Modules/_json.c:745`) builds `rval` (a dict or a `pairs`
list) while, per key, interning through the shared `memo` dict, and finally calls
`s->object_pairs_hook`/`object_hook` (`:858`) on the assembled result.

**Reasoning.** The `object_pairs_hook`/`object_hook` (and a key object's `__eq__`/`__hash__`
during `memo` interning) run arbitrary Python and can reach back into the scanner state or the
shared `memo`, clearing or replacing entries the outer parse still references; a borrowed
`pairs`/key pointer used after the hook returns can be stale.

**Why it fits.** Borrowed intermediate container/key held across a user hook that can mutate the
shared parse state (`#143635` shared-argument-list-cleared shape).

**Reachability.** `json.loads(s, object_pairs_hook=cb)` (or `object_hook`) where `cb` mutates a
captured reference to the scanner / a prior partially-built object; deeply nested objects sharing
the `memo`.

**Trigger hypothesis.** A hook stashed on the first nested object clears the shared `memo`/prior
`pairs` while a parent `_parse_object_unicode` frame still holds a borrowed pointer into it.

**Confidence & dup-check.** **Low-medium (open).** The scanner mostly owns its locals, so the
sharp case is the shared `memo` dict across recursion. Verify `memo` accesses re-lookup rather
than caching a borrowed value across a hook. `git log --grep "_json.*memo\|object_pairs_hook"` —
none reentrancy-related. Distinct from audit7's `json.dumps` encoder-`default` site (this is the
*decode* side).
</content>

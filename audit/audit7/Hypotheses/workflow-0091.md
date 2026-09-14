# workflow-0091 — Error-path ownership loss (leak of an owned intermediate)

> An operation acquires an owned intermediate (converted value, builder, list/tuple, callback
> result, allocation) before all fallible validation completes, then an exceptional exit
> (early return, wrong `goto` label, shadowed variable) fails to release it.

10 fresh sites. Detection: release build lacks `sys.gettotalrefcount`; re-run with
`ASAN_OPTIONS=detect_leaks=1` (LSan) or watch RSS / `tracemalloc` deltas over N iterations. A
double-free / UAF on the error path (not a mere leak) is the higher-value outcome and aborts
under ASan. Force failures with `_testcapi.set_nomemory(k, k+1)` (no ctypes).

---

## Site 1 — `socket.getnameinfo` result build on a mid-build failure

**Site.** `socket_getnameinfo` (`Modules/socketmodule.c`) resolves an address, allocates owned
temporaries (host/serv buffers → `PyUnicode`), then `Py_BuildValue`s the result tuple; an
allocation or decode failure after the first owned string exists must release it.

**Reasoning.** Between building `host` and `serv` (or on `Py_BuildValue` failure), an early
`return NULL` that skips a `Py_DECREF(host)` leaks the first string.

**Why it fits.** Owned intermediate created before a later fallible step; error exit before
finalization.

**Reachability.** `socket.getnameinfo(addr, flags)`; inject OOM at the 2nd owned allocation via
`set_nomemory`.

**Trigger hypothesis.** `set_nomemory` fails the `serv` unicode alloc after `host` is built;
check the error path decrefs `host`. Repeat N times, watch RSS.

**Confidence & dup-check.** Low-medium. getaddrinfo (original set) was the classic; getnameinfo
is the less-audited sibling. `git log --grep "getnameinfo leak"`.

---

## Site 2 — `datetime.time.fromisoformat` owned `tzinfo` temp before range reject

**Site.** `datetime_time_fromisoformat_impl` (`Modules/_datetimemodule.c:5194`) and the date
variant (`:3424`) parse components, build an owned `tzinfo`/`timedelta` temp
(`parse_isoformat_time` → `new_fixed_offset`/`tzinfo_from_isoformat_results`), then run final
range validation.

**Reasoning.** A string that parses structurally (allocating the tz temp) but fails a later
range check (`microsecond`/offset bounds) must `Py_DECREF` the tz temp on the reject path.

**Why it fits.** Decode-then-reject: an owned decoded value created before the failing check.

**Reachability.** `datetime.time.fromisoformat("00:00:00+99:99")` /
`"...+10:00:00.999999999"` — valid structure, out-of-range offset.

**Trigger hypothesis.** Craft a string that builds the fixed-offset tzinfo then trips a bound;
verify the reject `goto` decrefs `tzinfo`. Repeat / refcount-delta.

**Confidence & dup-check.** Low-medium. The C parser mostly uses stack ints; the owned tz temp
on the reject path is the spot. Compare `#139751`.

---

## Site 3 — `_ssl` `_get_peer_alt_names` / SAN list build on a malformed extension

**Site.** `_get_peer_alt_names` (`Modules/_ssl.c`) builds a list of `(type, value)` tuples from
X.509 subjectAltName entries; per-entry it allocates an owned tuple/strings then appends.

**Reasoning.** A GENERAL_NAME whose conversion fails mid-build must decref the partial list *and*
the current entry; a `goto fail` that misses the current owned tuple leaks it.

**Why it fits.** Builder pattern: owned container + accumulated entries, error before
finalization (`#139988` shape).

**Reachability.** `ssl._ssl._test_decode_cert(path)` on a crafted cert with a malformed SAN
entry (e.g. an otherName type the converter rejects).

**Trigger hypothesis.** Malformed alt-name after several valid ones; verify the fail path frees
the list and current tuple. Repeat.

**Confidence & dup-check.** Low. Requires a crafted cert; `_ssl` is careful. Distinct from the
original set's `_decode_certificate` (this is the SAN sub-builder). Ruling-out lead.

---

## Site 4 — `_pickle` `save_reduce` owned state/listitems/dictitems on error (dump side)

**Site.** `save_reduce` (`Modules/_pickle.c`) receives the `__reduce__` 2–6 tuple and holds
owned references to `state`, `listitems`, `dictitems`, `callable`, `argtup`; a failure while
emitting one component must release the rest.

**Reasoning.** After validating the reduce tuple, several owned sub-objects exist; a write error
(buffer/`persistent_id`/`memo` failure) on component *k* must decref components *k+1..n*.

**Why it fits.** Multiple owned intermediates across fallible emit steps; error exit skips some
releases.

**Reachability.** `pickle.dumps(evil)` where `evil.__reduce__` returns a 6-tuple; inject a write
failure via a file object whose `write` raises after the first component, or `set_nomemory`.

**Trigger hypothesis.** `__reduce__` returns `(cls, args, state, listiter, dictiter)`; fail the
emit of `listitems`; verify `state`/`dictitems` are decref'd. Repeat.

**Confidence & dup-check.** Low-medium. The dump side is less leak-audited than load
(`#140406`). Map each `goto error` in `save_reduce`.

---

## Site 5 — `csv.writer.writerow` per-field rec buffer / temp on a mid-row failure

**Site.** `csv_writerow` / `join_append_data` (`Modules/_csv.c`) coerce each field with
`str()`/`PyObject_Str` (owned temp) and grow the internal `rec` buffer; a failure after a field's
owned string exists must release it.

**Reasoning.** If `join_append` fails (buffer realloc OOM) after `PyObject_Str(field)` produced
an owned string, an early return that skips `Py_DECREF(field_str)` leaks it.

**Why it fits.** Owned per-iteration temp not released on the error branch.

**Reachability.** `csv.writer(f).writerow([obj, ...])`; `set_nomemory` on the `rec` realloc after
a field is coerced.

**Trigger hypothesis.** Fail the buffer growth after `str(field)`; verify the coerced string is
decref'd. Repeat.

**Confidence & dup-check.** Low. `_csv` is fairly tight; confirm the field temp lifetime on the
realloc-failure branch.

---

## Site 6 — `_asyncio` `task_step` / future result owned temp on error

**Site.** `task_step_impl` (`Modules/_asynciomodule.c`) obtains an owned `result` from the
coroutine `send`/`throw`, then inspects it (blocking future, bare yield, etc.); several branches
build owned temporaries (e.g. a wrapper future, an exception) before a fallible publish.

**Reasoning.** A branch that raises after creating an owned temp (e.g. `_asyncio_future_blocking`
handling that allocates then hits an error) must release it.

**Why it fits.** Owned intermediate created before a fallible step in a multi-branch dispatch.

**Reachability.** Drive a Task with a coroutine that yields a crafted awaitable (custom
`__await__`) triggering the error branch; optionally `set_nomemory`.

**Trigger hypothesis.** A yielded object that passes the first check then fails a later one after
a temp is built; watch refcounts across many task steps.

**Confidence & dup-check.** Low-medium. asyncio is heavily hardened; the leak axis (vs. UAF) is
less audited. Ruling-out lead.

---

## Site 7 — `os.getgrouplist` / `os.sched_getaffinity` result-list build on error

**Site.** `os_getgrouplist_impl` / `os_sched_getaffinity_impl` (`Modules/posixmodule.c`) allocate
a C array, call the syscall, then build a Python `list`/`set` appending owned `int`s; a mid-build
append/alloc failure must free the partial container.

**Reasoning.** Classic builder: `list` created, N ints appended, then an OOM on int *k* must
decref the list (and it does — but verify the C array and any owned temp are also freed).

**Why it fits.** `#139988` builder pattern; owned container + accumulated values.

**Reachability.** `os.getgrouplist(user, group)` / `os.sched_getaffinity(0)` with `set_nomemory`
at the k-th int.

**Trigger hypothesis.** Fail the int alloc after the list + several entries exist; verify list
and C buffer freed. Repeat.

**Confidence & dup-check.** Low. These are simple loops; ruling-out. `git log --grep
"sched_getaffinity"`.

---

## Site 8 — `itertools.groupby` / `_grouper` construction owned temp on error

**Site.** `groupby_new` / `_grouper_create` (`Modules/itertoolsmodule.c`) store owned
`it`/`keyfunc`/`tgtkey`/`currkey`/`currvalue`; a failure between acquiring the source iterator and
finishing initialization must release the already-owned fields.

**Reasoning.** After `PyObject_GetIter(iterable)` (owned) and `Py_INCREF(keyfunc)`, an allocation
failure in `PyObject_New`/tuple build must decref both.

**Why it fits.** Resource acquired before validation/allocation completes; error return without
release (`#148484` shape).

**Reachability.** `itertools.groupby(iterable, key)`; `set_nomemory` on the object allocation
after the iterator is obtained.

**Trigger hypothesis.** Fail the `groupby` object alloc after `GetIter` succeeded; verify the
iterator ref is dropped. Repeat.

**Confidence & dup-check.** Low. itertools ctors are usually tidy; ruling-out. (Note groupby's
FT-iteration is a separate #123471 concern — this is the *construction leak* axis only.)

---

## Site 9 — `_elementtree` `Element.__deepcopy__` / `__setstate__` children on error

**Site.** `element_deepcopy` / `element_setstate_from_*` (`Modules/_elementtree.c`) allocate a new
`extra->children` array and deep-copy each child (owned) into it; a copy failure mid-array must
free the already-copied children and the array.

**Reasoning.** After copying *k* children into the new array, a `deepcopy` failure on child *k+1*
must decref children `0..k` and the array; a bare `goto error` that only frees the array leaks
the copied children.

**Why it fits.** Partial builder (child array) on a fallible per-element copy.

**Reachability.** `copy.deepcopy(element)` where a child's deepcopy raises (a custom attrib value
whose `__deepcopy__` raises), or `set_nomemory` mid-array.

**Trigger hypothesis.** Child *k+1* deepcopy raises; verify children `0..k` are released. Repeat
/ RSS delta.

**Confidence & dup-check.** Low-medium. `_elementtree`'s reentrancy UAFs were fixed
(gh-126033/143200) but the deepcopy/setstate *leak* axis is separate. Audit the error labels.

---

## Site 10 — `_json` `c_make_encoder` / encoder `default` owned result on error

**Site.** The C encoder (`Modules/_json.c`) obtains an owned `newobj` from `default(obj)` and
then recursively encodes it; if the recursive encode fails, or a markers/circular-ref check
fires *after* `default` returned, the owned `newobj` must be released.

**Reasoning.** `default` result is owned; a subsequent circular-reference `PyErr_SetString` /
recursion-limit error that returns without decref leaks it.

**Why it fits.** Owned callback result before a fallible validation (`#140406`/`#139988` shape).

**Reachability.** `json.dumps(x, default=cb)` where `cb` returns an object that then fails
encoding (e.g. a self-referential container to trip circular detection).

**Trigger hypothesis.** `default` returns a list containing itself → circular-ref error after the
owned result exists; verify it is decref'd. Repeat.

**Confidence & dup-check.** Low-medium. Compare `#142831` scope. Map the `default`-branch error
exits for a missing decref.
</content>

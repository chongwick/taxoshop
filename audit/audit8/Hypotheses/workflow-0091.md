# workflow-0091 — Error-path ownership loss (leak / double-free of an owned intermediate)

> An operation acquires an owned intermediate (converted value, builder list/tuple, callback
> result, allocation, iterator) before all fallible validation completes, then an exceptional
> exit (early return, wrong `goto` label, shadowed variable) fails to release it — or releases it
> twice.

10 fresh sites (distinct from audit7). Detection: release build lacks `sys.gettotalrefcount`;
re-run with `ASAN_OPTIONS=detect_leaks=1` (LSan) or watch RSS / `tracemalloc` deltas over N
iterations. A **double-free / UAF** on the error path (not a mere leak) is the higher-value,
ASan-visible outcome. Force failures with `_testcapi.set_nomemory(k, k+1)` — **no `ctypes`**.

---

## Site 1 — `grp.getgrall` / `mkgrent` per-group member-list build on a mid-build failure

**Site.** `grp_getgrall_impl` (`Modules/grpmodule.c:302`) loops `while ((p = getgrent()))`
calling `mkgrent(p)`, which builds a members `list` (`PyList_New(0)` at `:76`) and a `struct_group`
tuple; a failure while appending a member or building the tuple must free the partial members list
and the accumulated result list.

**Reasoning.** After `mkgrent` has allocated the members list and appended *k* names, an OOM on
name *k+1* (or on the enclosing `PyList_Append`) must decref the members list and the entry — a
bare `goto` that frees only the outer list leaks the members list.

**Why it fits.** Nested builder (result list of per-group tuples, each owning a members list) with
a fallible per-element step (`#139988` builder shape).

**Reachability.** `grp.getgrall()` with `_testcapi.set_nomemory(k, k+1)` sweeping `k`.

**Trigger hypothesis.** Fail the member-`str` alloc after several members exist; verify the
members list + partial result are freed. Repeat / RSS delta.

**Confidence & dup-check.** **Low-medium.** getgrall itself is thread-guarded (`group_db_mutex`),
but the *leak* axis on `mkgrent`'s error labels is separate. `git log --grep "getgrall\|mkgrent"`.

---

## Site 2 — `_struct.Struct.unpack` (`s_unpack_internal`) result tuple on a mid-field failure

**Site.** `s_unpack_internal` (`Modules/_struct.c:2054`) builds a result `tuple`, unpacking each
field via its `unpack` function (which allocates owned `int`/`bytes`/`float` objects) and
`PyTuple_SET_ITEM`ing them.

**Reasoning.** After *k* fields are set into the tuple, a failure unpacking field *k+1* (e.g. an
OOM allocating a `PyLong`, or a custom-format decode error) must decref the partially-filled
tuple; an early `return NULL` that skips it leaks the tuple and its *k* items.

**Why it fits.** Owned container + accumulated owned elements before a fallible per-field step.

**Reachability.** `struct.Struct(fmt).unpack(buf)` (or `struct.unpack`) with
`_testcapi.set_nomemory` at the k-th field alloc.

**Trigger hypothesis.** Fail the alloc of field *k+1*; verify the result tuple (holding fields
`0..k`) is decref'd on the error exit. Repeat.

**Confidence & dup-check.** **Low-medium.** `_struct` is fairly tight, but the many field-type
branches in `s_unpack_internal` each have an error exit worth mapping. `git log --grep
"s_unpack\|struct.*leak"`.

---

## Site 3 — `_zoneinfo` `load_data` transition/type lists on a parse or alloc failure

**Site.** `load_data` (`Modules/_zoneinfo.c:967`) calls `state->_common_mod.load_data` (`:986`)
and builds arrays/lists of transitions, types, and abbreviations into the `ZoneInfo` object; a
failure partway through must release the already-built intermediates.

**Reasoning.** After allocating the transitions array and several `_ttinfo`/abbr objects, a later
parse error or OOM must free them; a `goto error` that frees only some intermediates leaks the
rest.

**Why it fits.** Multi-step builder over parsed TZif data with fallible allocations
(`#148484`/#139988 shape).

**Reachability.** `zoneinfo.ZoneInfo.from_file(io.BytesIO(crafted_tzif))` with a structurally-
valid header but a truncated/invalid body, or `set_nomemory` mid-parse.

**Trigger hypothesis.** Trip an allocation failure after the transitions array + some `_ttinfo`s
exist; verify all are released. Repeat / RSS delta.

**Confidence & dup-check.** **Low-medium.** audit6 covered the zoneinfo *strong-cache UAF*
(#142782); the *parse-error leak* axis in `load_data` is distinct. `git log --grep
"zoneinfo.*leak\|load_data"`.

---

## Site 4 — `itertools.product.__new__` (`product_new`) accumulated pool tuples on error

**Site.** `product_new` (`Modules/itertoolsmodule.c:2069`) converts each input iterable to an
owned pool `tuple` and stores them in a `pools` tuple/array, plus a `repeat` handling path; a
failure mid-conversion must free the pools acquired so far.

**Reasoning.** After building pool tuples for arguments `0..k`, an error converting argument *k+1*
(e.g. a non-iterable, or OOM in `PySequence_Tuple`) must decref pools `0..k` and the array; a bare
error return leaks them.

**Why it fits.** Owned intermediates accumulated before validation of all arguments completes
(audit7 covered `groupby`; `product`/`permutations`/`combinations` ctors are distinct).

**Reachability.** `itertools.product(iter0, iter1, BadArg)` where `BadArg` is non-iterable or
triggers `set_nomemory` during its `PySequence_Tuple`.

**Trigger hypothesis.** Fail argument *k+1*'s tuple build; verify pools `0..k` are freed. Repeat.

**Confidence & dup-check.** **Low.** itertools ctors are usually tidy; ruling-out. `git log
--grep "product_new\|itertools.*leak"`.

---

## Site 5 — `_json` scanner `_parse_object_unicode` owned `pairs`/`rval` on a hook or parse failure

**Site.** `_parse_object_unicode` (`Modules/_json.c:745`) builds an owned `rval` dict (or a
`pairs` list when `object_pairs_hook` is set), accumulating owned key/value objects, then calls
`object_pairs_hook`/`object_hook` (`:858`); a parse error mid-object, or a rejecting hook, must
release the accumulated intermediates.

**Reasoning.** After several key/value pairs are decoded (owned) into `pairs`/`rval`, a malformed
tail token or a hook that raises must decref them; an error `goto` that misses the current
key/value or the `pairs` list leaks them.

**Why it fits.** Owned builder + accumulated owned entries before a fallible finalization step
(`#139988`/`#140406` shape).

**Reachability.** `json.loads('{"a":1,"b":')` (truncated) or `json.loads(s,
object_pairs_hook=cb)` where `cb` raises after valid pairs exist; `set_nomemory` mid-parse.

**Trigger hypothesis.** Feed a truncated object after several pairs; verify `pairs`/current
key/value are all released on the parse-error exit. Repeat / RSS delta.

**Confidence & dup-check.** **Low-medium.** The scanner has many error exits per token. Map the
`goto`/`return NULL` after each owned key/value acquisition. `git log --grep "_json.*leak\|
parse_object"`.

---

## Site 6 — `socket.recvmsg` ancillary-data list build (`makeval_recvmsg`) on error

**Site.** `sock_recvmsg_guts` (`Modules/socketmodule.c:4375`) drives `recvmsg`, then
`makeval_recvmsg` (`:4508`) builds the returned data `bytes` and the ancillary-data `list` of
`(cmsg_level, cmsg_type, cmsg_data)` tuples; a failure while building an ancillary tuple must free
the partial list and the current tuple.

**Reasoning.** After appending *k* ancillary tuples, an OOM or conversion error on cmsg *k+1* must
decref the list and the current owned components; a bare error return leaks them.

**Why it fits.** Builder over kernel-returned control messages with per-item owned allocations
(`#139988`).

**Reachability.** A `socketpair()` with sent ancillary data (e.g. `SCM_RIGHTS`) so `recvmsg`
returns cmsgs; `set_nomemory` at the k-th ancillary tuple alloc.

**Trigger hypothesis.** Fail the cmsg-data `bytes` alloc after several cmsgs; verify the list +
partial tuple are freed. Repeat.

**Confidence & dup-check.** **Low.** Needs an ancillary-data setup; `_socket` is careful. Map the
error exits in `makeval_recvmsg`/`sock_recvmsg_guts`. `git log --grep "recvmsg"`.

---

## Site 7 — `select.epoll.poll` result-list build on a mid-build failure

**Site.** `select_epoll_poll_impl` (`Modules/selectmodule.c:1613`) allocates
`elist = PyList_New(nfds)` (`:1704`) then, per ready fd, builds an `etuple = (fd, events)` and
`PyList_SET_ITEM(elist, i, etuple)` (`:1715`); a failure building `etuple` *i* must free `elist`
(which holds tuples `0..i-1`).

**Reasoning.** After *i* tuples are placed, an OOM building the `PyLong` for fd/events *i* must
decref `elist`; a `goto error` that misses it (or double-frees an already-SET_ITEM'd tuple) is the
defect.

**Why it fits.** Preallocated result container filled with owned per-item tuples across a fallible
per-item build (`#148484` shape).

**Reachability.** An epoll with many ready fds (register several ready pipes) + `set_nomemory` at
the i-th tuple's `PyLong` alloc.

**Trigger hypothesis.** Fail the fd `PyLong` alloc at item *i*; verify `elist` and any half-built
`etuple` are released exactly once. Repeat.

**Confidence & dup-check.** **Low.** Preallocated-list fill is a common tidy pattern; verify the
`etuple` half-build (one `SET_ITEM` done, second alloc fails) frees the first component. `git log
--grep "epoll.*poll"`.

---

## Site 8 — `_pickle` `load_build` / `load_reduce` owned intermediates on the error path (leak axis)

**Site.** `load_build` (`Modules/_pickle.c:6961`), `load_reduce` (`:7099`), `load_appends`
(`:6848`), `load_setitems` (`:6898`) pop owned objects off the unpickler stack and invoke
`__setstate__`/`obj.append`/`obj.__dict__` updates; a failure after popping owned state must
release it.

**Reasoning.** `load_build` obtains an owned `state` (and possibly `slotstate`) before applying
it; if `__setstate__` raises or an attribute update fails, the owned `state`/`slotstate` must be
decref'd — a direct `return -1` that skips it leaks the intermediate.

**Why it fits.** Owned intermediate acquired before a fallible callback/update step
(`#140406`/#140593 shape). audit5 covered the *reentrancy UAF* on the shared stack; this is the
distinct *error-path leak* axis.

**Reachability.** `pickle.loads(payload)` with a crafted `BUILD`/`REDUCE` opcode whose target's
`__setstate__`/`append` raises (custom class), or `set_nomemory` after the state is popped.

**Trigger hypothesis.** Make `__setstate__` raise after `load_build` popped `state`; verify
`state`/`slotstate` are released. Repeat / RSS delta.

**Confidence & dup-check.** **Low-medium.** The load side is more scrutinized for UAF than for
leaks. Map each `goto`/`return -1` after an owned pop in these four handlers. `git log --grep
"load_build\|load_reduce"`.

---

## Site 9 — `os.getgroups` (`os_getgroups_impl`) result-list build on error

**Site.** `os_getgroups_impl` (`Modules/posixmodule.c:9802`) calls `getgroups()` into a C array,
then builds a Python `list` appending owned `PyLong`s; a mid-build append/alloc failure must free
the partial list (and the C array).

**Reasoning.** Classic builder: after appending *k* gids, an OOM on gid *k+1* must decref the
list; verify the C `gid_t` buffer is also freed on every exit.

**Why it fits.** Owned container + accumulated owned values (`#139988`).

**Reachability.** `os.getgroups()` with `set_nomemory` at the k-th `PyLong` alloc.

**Trigger hypothesis.** Fail the int alloc after the list + several entries exist; verify list +
C buffer freed. Repeat.

**Confidence & dup-check.** **Low.** Simple loop; ruling-out. audit7 OOM-swept `getgrouplist`/
`sched_getaffinity` (distinct syscalls). `git log --grep "getgroups"`.

---

## Site 10 — `_ssl` `_get_aia_uri` (Authority Information Access) URI-list build on a malformed extension

**Site.** `_get_aia_uri` (`Modules/_ssl.c:1563`, called from `:1805`/`:1816` for OCSP and CA
issuers) walks the AUTHORITY_INFO_ACCESS extension building a tuple/list of owned URI strings; a
per-entry conversion failure must release the partial list and the current entry.

**Reasoning.** After converting *k* AIA URIs, a malformed GENERAL_NAME (or OOM) on entry *k+1*
must decref the list and the current owned string; a `goto fail` that misses one leaks it.

**Why it fits.** Builder over X.509 extension entries with owned per-entry allocations
(`#139988`); the AIA sub-builder is distinct from audit7's `_get_peer_alt_names` (SAN) site
(`:1302`).

**Reachability.** `ssl._ssl._test_decode_cert(path)` on a cert with a crafted AIA extension
(several valid OCSP URIs then a malformed accessLocation).

**Trigger hypothesis.** Malformed AIA entry after valid ones; verify the list + current URI are
freed on the fail path. Repeat.

**Confidence & dup-check.** **Low.** Requires a crafted cert; `_ssl` is careful. Distinct
extension from the SAN builder. `git log --grep "_get_aia_uri\|authority information"`.
</content>

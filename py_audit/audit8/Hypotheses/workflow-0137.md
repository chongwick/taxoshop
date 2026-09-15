# workflow-0137 — Reentrant argument conversion invalidates a backing resource

> A native operation retains a borrowed pointer, cached size, or backing-resource handle across a
> user-code boundary reached *through argument conversion* (`__index__`, `__float__`,
> `__buffer__`, `fileno()`, factory/converter callbacks). The user code detaches/closes/resizes
> that resource, but the operation resumes using its pre-bound handle.

10 fresh sites (no audit7 file existed for this family). **Key structural note:** Argument
Clinic runs `__index__`/`GetBuffer` converters in the *wrapper*, **before** the impl captures
`self`'s native state — this defuses the classic "capture-then-convert" shape for clinic
functions. The genuinely-open leads here (⭐) exploit **PEP-688 `__buffer__` reentrancy**:
`PyObject_GetBuffer(arg)` runs `arg.__buffer__` (arbitrary Python) which can free a *different*
`self->resource` that Clinic cannot protect.

---

## Site 1 — `_ssl.SSLSocket.write(b)` — `b.__buffer__` frees `self->ssl` before `SSL_write`  ⭐

**Site.** `_ssl__SSLSocket_write_impl` (`Modules/_ssl.c:2761`) receives an already-acquired
`Py_buffer *b` and then calls `SSL_write(self->ssl, b->buf, ...)`. The `Py_buffer` was obtained
by the Clinic wrapper via `PyObject_GetBuffer(b)` → runs `b.__buffer__`.

**Reasoning.** A PEP-688 buffer object's `__buffer__` is arbitrary Python. If it closes /
`unwrap`s / reinitializes the `SSLSocket` (dropping/freeing the underlying `SSL*`) *while
returning a valid buffer for `b`*, the impl then calls `SSL_write` through a freed `self->ssl`.
Clinic cannot guard this because the freed resource (`self->ssl`) is unrelated to the buffer arg.

**Why it fits.** Backing resource handle (`self->ssl`) captured/assumed-valid across a conversion
callback (`GetBuffer`→`__buffer__`) that frees it (`#143378` buffer-acquisition-runs-user-code
shape).

**Reachability.** `s.write(EvilBuf())` where `EvilBuf.__buffer__` triggers teardown of the SSL
layer (e.g. re-wrapping/closing the socket) then returns `memoryview(b"x")`.

**Trigger hypothesis.** `__buffer__` forces `self->ssl` to be freed/replaced; `SSL_write`
dereferences the stale pointer.

**Confidence & dup-check.** **Medium (open).** `git log --grep "_ssl.*buffer\|SSLSocket.*write"`
shows no reentrancy fix. Verify whether `_ssl__SSLSocket_write_impl` re-validates `self->ssl`
after the buffer is bound (it likely checks once at entry, *before* nothing — the check precedes
the write but the buffer/`ssl` interleave is the question). Confirm a Python path can free `ssl`
while `self` stays alive.

---

## Site 2 — `_ssl.SSLSocket.read(len, buffer)` — `len.__index__` / `buffer.__buffer__` frees `self->ssl`  ⭐

**Site.** `_ssl__SSLSocket_read_impl` (`Modules/_ssl.c:2898`) takes `Py_ssize_t len` and an
optional writable `buffer`, then reads via `SSL_read(self->ssl, ...)` into the buffer.

**Reasoning.** With the two-arg form, Clinic converts `len` (`__index__`) and acquires `buffer`
(`__buffer__`) before the impl. Either callback can tear down the SSL layer; the impl then
`SSL_read`s through a freed `self->ssl` or into a buffer whose exporter was freed.

**Why it fits.** Resource handle + destination buffer assumed valid across conversion callbacks
that can free them (`#143007`/`#143378`).

**Reachability.** `s.read(EvilLen(), bytearray(64))` where `EvilLen.__index__` closes/re-wraps
the SSL layer; or `s.read(64, EvilBuf())`.

**Trigger hypothesis.** `EvilLen.__index__` frees `self->ssl`; `SSL_read` uses the stale pointer.

**Confidence & dup-check.** **Medium (open).** Same dup-check as Site 1. Distinct because `read`
also has a writable-buffer detach axis. Confirm `SSLSocket` exposes a Python-reachable operation
that frees `ssl` without dropping `self`.

---

## Site 3 — `_sqlite3.Blob.write(data)` — `data.__buffer__` closes the blob before `sqlite3_blob_write`  ⭐

**Site.** `blob_write_impl` (`Modules/_sqlite/blob.c:258`) receives `Py_buffer *data` (from
Clinic `GetBuffer`) then calls `sqlite3_blob_write(self->blob, data->buf, ...)` (`:234`).

**Reasoning.** `data.__buffer__` can call `blob.close()` / `connection.close()`, which
`sqlite3_blob_close`s and NULLs `self->blob`; if the entry validity check ran *before* the
conversion (or is not re-done after), `sqlite3_blob_write` uses a freed/closed blob handle.

**Why it fits.** Backing resource (`self->blob`) invalidated by an argument-conversion callback
(`#143198`/`#143380` sqlite-connection-closed-during-conversion shape).

**Reachability.** `blob.write(EvilBuf())` where `EvilBuf.__buffer__` calls `blob.close()`.

**Trigger hypothesis.** `__buffer__` closes the connection; `sqlite3_blob_write` runs on the
closed blob.

**Confidence & dup-check.** **Medium (open).** Recent Blob fixes were about *slices*
(#150449/#155702/#150913), not `__buffer__` reentrancy. Verify `blob_write_impl` calls
`pysqlite_check_blob(self)` **after** the buffer is bound (Clinic binds it first, so the entry
check sees a possibly-already-closed blob → clean error only if re-checked at the right point).
`git log --grep "sqlite.*blob.*close\|blob.*reentr"`.

---

## Site 4 — `_sqlite3.Blob.read(length)` — `length.__index__` closes the blob before `sqlite3_blob_read`

**Site.** `blob_read_impl` (`Modules/_sqlite/blob.c:192`) takes `int length` (Clinic
`__index__`), allocates a result `bytes`, then `sqlite3_blob_read(self->blob, buf, length,
offset)` (`:151`).

**Reasoning.** `length.__index__` (converted before the impl) can `blob.close()`/`con.close()`,
freeing `self->blob`; if the impl assumes the blob validated at call entry, the read runs on a
closed handle.

**Why it fits.** Resource handle invalidated by numeric-argument conversion (core 0137 shape,
`#143007`).

**Reachability.** `blob.read(EvilLen())` where `EvilLen.__index__` calls `blob.close()`.

**Trigger hypothesis.** `__index__` closes the blob; `sqlite3_blob_read` dereferences freed
`self->blob`.

**Confidence & dup-check.** **Low-medium (ruling-out-leaning).** Clinic ordering means the
`pysqlite_check_blob` inside the impl runs *after* `__index__`, so it likely catches the closed
blob and raises cleanly — verify the check is present and precedes the `sqlite3_blob_read`. audit3
covered blob *subscript* (index/slice); `.read()` is the distinct method. `git log --grep
"blob_read"`.

---

## Site 5 — `_sqlite3.Blob.seek(offset, origin)` — `offset.__index__` closes the blob

**Site.** `blob_seek_impl` (`Modules/_sqlite/blob.c:290`) takes `int offset` and computes a new
position against `sqlite3_blob_bytes(self->blob)`.

**Reasoning.** `offset.__index__` can close the blob/connection before the impl reads
`sqlite3_blob_bytes(self->blob)`; a missing re-check dereferences the freed handle.

**Why it fits.** Resource handle invalidated by argument conversion.

**Reachability.** `blob.seek(EvilOffset())` where `EvilOffset.__index__` calls `con.close()`.

**Trigger hypothesis.** `__index__` closes the blob; `sqlite3_blob_bytes` reads freed state.

**Confidence & dup-check.** **Low-medium (ruling-out-leaning).** Same Clinic-ordering guard
question as Site 4. Verify `pysqlite_check_blob` runs before the `sqlite3_blob_bytes` read. `git
log --grep "blob_seek"`.

---

## Site 6 — `mmap.__setitem__` value `__index__` after slice bounds captured

**Site.** `mmap_ass_subscript` (`Modules/mmapmodule.c:1658` int index, `:1680` slice) computes
the target index/slice against the current size and captures `self->data`, then converts the RHS
value via `PyNumber_AsSsize_t(value, ...)` and writes.

**Reasoning.** The value's `__index__` runs after bounds/pointer capture and can `mmap.resize()`,
which `mremap`s (moves/shrinks) the mapping; the subsequent write goes to the stale `self->data`
/ out-of-bounds offset.

**Why it fits.** Cached buffer pointer + bounds held across a value-conversion callback that
resizes the backing (the canonical 0137 mmap shape).

**Reachability.** `m[i] = Evil()` where `Evil.__index__` calls `m.resize(1)`.

**Confidence & dup-check.** **DUP — do not re-file.** This is `#157335` (mmap `__setitem__`
reentrant resize), already reported upstream and recorded in `STARTUP.md`/audit2-3
(`DUPLICATE-002`). Listed here only to keep the mmap corner explicit and to check the *slice*-
assignment variant against the same fix.

---

## Site 7 — `select.select(rlist, wlist, xlist)` — `fileno()` mutates the fd list mid-scan

**Site.** `seq2set` (`Modules/selectmodule.c:145`, called from `select_select_impl:279`) iterates
a `PySequence_Fast` of each list calling `PyObject_AsFileDescriptor(o)` (`:168`) → the object's
`fileno()` (arbitrary Python) per element.

**Reasoning.** `fileno()` can `list.clear()`/reassign the very list being scanned, freeing/
reallocating the `ob_item` array that `PySequence_Fast_GET_ITEM` reads.

**Why it fits.** Borrowed sequence storage traversed across a per-element conversion callback
(`fileno()`) that mutates the sequence (`#144128` element-index-conversion-clears-source-list
shape).

**Reachability.** `select.select([EvilFd()], [], [])` where `EvilFd.fileno()` clears the list.

**Trigger hypothesis.** `fileno()` clears the list on element 0; element 1 reads freed `ob_item`.

**Confidence & dup-check.** **Low (ruling-out).** Verified guarded: `seq2set` `Py_INCREF(o)`
before `fileno()` (comment: "any intervening fileno() calls could decr this refcnt") and the loop
re-reads `PySequence_Fast_GET_SIZE` each iteration, so a shrink terminates the loop and a grow
reads the current array. Cross off; documents the correct pattern. `git log --grep "seq2set"`.

---

## Site 8 — `select.epoll.poll(timeout, maxevents)` — `maxevents.__index__` closes the epoll fd

**Site.** `select_epoll_poll_impl` (`Modules/selectmodule.c`, near the `self->epfd < 0` checks at
`:1461`/`:1477`) takes `maxevents` (converted via `__index__`) and calls `epoll_wait(self->epfd,
...)`.

**Reasoning.** `maxevents.__index__` can call `epoll.close()`, which sets `self->epfd = -1` (and
`close()`s the real fd); `epoll_wait` then runs on `-1`/a recycled fd.

**Why it fits.** Backing resource handle (`epfd`) invalidated by numeric-argument conversion.

**Reachability.** `ep.poll(0, EvilMax())` where `EvilMax.__index__` calls `ep.close()`.

**Trigger hypothesis.** `__index__` closes the epoll; `epoll_wait(-1, ...)` → `EBADF`, or worse
if the fd number was recycled by another thread.

**Confidence & dup-check.** **Low (weak — EBADF, not UAF).** `epfd` is an `int`, so closing gives
a defined error rather than a memory bug (Clinic also converts `maxevents` before the impl re-
reads `epfd`). Kept as a lead for the fd-recycling angle. `git log --grep "epoll.*poll"`.

---

## Site 9 — `_hashlib` `HASH.update(data)` — `data.__buffer__` reinitializes `self->ctx`  ⭐

**Site.** `_hashlib` digest `update` (`Modules/_hashopenssl.c`, `GetBuffer` sites around
`:993`/`:1316`/`:2245`) acquires `Py_buffer view` from `data` then `EVP_DigestUpdate(self->ctx,
view.buf, view.len)`.

**Reasoning.** `data.__buffer__` (PEP-688) is arbitrary Python and can re-enter the same hash
object — e.g. `h.copy()` semantics, or an operation that frees/reinitializes `self->ctx` — while
returning a valid buffer; `EVP_DigestUpdate` then runs on a freed/replaced `EVP_MD_CTX`.

**Why it fits.** Backing crypto context (`self->ctx`) assumed valid across a `GetBuffer` callback
that can invalidate it (`#144922` write-callback-reallocs-after-caching shape).

**Reachability.** `h = hashlib.sha256(); h.update(EvilBuf())` where `EvilBuf.__buffer__` reaches
into `h` to free/replace its context.

**Trigger hypothesis.** `__buffer__` triggers a context teardown on `h`; `EVP_DigestUpdate`
dereferences the freed `ctx`.

**Confidence & dup-check.** **Low-medium (open).** Requires a Python-reachable way to free
`self->ctx` while `self` stays alive (the digest object owns its ctx and there is no public
`close`), so likely safe — but the free-threaded `ENTER_HASHLIB`/mutex and the `__buffer__`
window are worth confirming. `git log --grep "_hashopenssl.*buffer\|EVP_DigestUpdate"`.

---

## Site 10 — `zlib`/`bz2`/`lzma` `Decompress.decompress(data, max_length)` — `data.__buffer__` / `max_length.__index__` frees `self->zst`

**Site.** `zlib_Decompress_decompress_impl` (`Modules/zlibmodule.c:882`) acquires `Py_buffer
data` and takes `Py_ssize_t max_length`, then feeds `self->zst.next_in = data.buf` and drives
`inflate` while growing the `_BlocksOutputBuffer`. (Same shape in `_bz2module.c` /
`_lzmamodule.c`.)

**Reasoning.** `data.__buffer__` or `max_length.__index__` (both converted by Clinic before the
impl) can re-enter the same decompressor (a reentrant `.decompress()`/`.flush()`), which mutates
`self->zst`/`unconsumed_tail` (`:1281`) the outer call still uses.

**Why it fits.** Cached stream state (`self->zst`) invalidated by an argument-conversion callback
that re-enters the operation (`#144922`).

**Reachability.** `d = zlib.decompressobj(); d.decompress(EvilBuf(), EvilMax())` where the
callback re-enters `d.decompress(...)`.

**Trigger hypothesis.** The conversion callback recursively calls `d.decompress`, advancing/
reallocating `self->zst.next_out`; the outer `inflate` writes through a stale pointer.

**Confidence & dup-check.** **Low (ruling-out-leaning).** The decompressor holds its own `zst`
(freed only on dealloc, and `self` is pinned by the call) and free-threaded builds take a per-
object lock; reentrancy on the same object under the GIL is the sharp case. Verify the impl re-
reads `self->zst` fields after any callout. `git log --grep "zlib.*reentr\|Decompress"`.
</content>

# audit9 — hunting a fresh CPython bug via the macro-taxonomies

Started 2026-09-21. Image `taxoshop/cpython-asan-ubsan:current` (ASan+UBSan, GIL build,
3.16.0a0, HEAD `e5d4fa28`). Read source from inside image (`/src/cpython`).

## Target families (from tally): 0137 reentrant conversion, 0080 callback reentrancy,
0014 borrowed handle, plus UBSan families 0005/0003/0007/0010.

## Ruled out so far (this audit)
- `_heapq` siftup/siftdown: HARDENED. After each RichCompareBool re-checks
  `size != PyList_GET_SIZE` (RuntimeError) AND refetches `arr = _PyList_ITEMS`.
- `_bisect` internal_bisect_right/left: SAFE. Uses `sq_item` (fresh ref + bounds check)
  per iteration; no cached raw pointer across compare.
- `_collections` deque count/contains/index/remove: HARDENED via `deque->state`
  mutation-counter checked after each compare, before re-deref of block `b`.

## Method: empirical evil-object battery across under-swept modules, run under ASan.

## RE-FIND (DUP, not new): sqlite3 callback_context heap-UAF via con.close() in callback
- progress_callback / authorizer_callback / trace_callback: con.close() inside the callback
  runs free_callback_contexts()->decref, and since sqlite keeps invoking the latched handler
  for the rest of the in-flight prepare/step (sqlite3_close_v2 = deferred zombie close), the
  next invocation increfs a freed callback_context. connection_close() never calls
  remove_callbacks() before sqlite3_close_v2.
- ASan: heap-use-after-free READ incref_callback_context connection.c:1137 (from
  progress_callback:1492 / authorizer_callback:1455); freed by free_callback_context<-
  decref_callback_context:1148<-callback:1507. Repros: repro/battery/t_sqlite_progress_close.py,
  t_sqlite_authorizer_close.py. Also aggregate/collation close => sqlite3_last_insert_rowid(NULL)
  (the #143662/db-NULL class).
- **DUP of OPEN #145040** ("_sqlite: NULL dereference when connection is closed from within a
  callback"). #151030 (closed as DUPLICATE of #145040) has the EXACT callback_context UAF writeup
  for authorizer/progress/trace. => confirmed re-find of an open bug, NOT new. Avoid this vein.

## Hardened (ruled out this audit, additional)
- lru_cache bounded/infinite: extensively reentrancy-hardened ("General note on reentrancy").
- sys.monitoring dispatch (instrumentation.c): tools bitmask is local copy + call_one re-checks
  NULL; line_data cached but lines is per-code, never moved, freed only in code_dealloc (code
  alive on stack). call_one_instrument borrowed instrument kept alive by executing frame.
- _asyncio future_schedule_callbacks: detaches fut_callbacks (ownership transfer) before iterate.
- select.seq2set: re-reads size + item each iter. csv writerow: iterator-based.
- list_richcompare: re-reads Py_SIZE + ob_item each iter (#120298 fixed).
- bytearray/list slice-assign fast paths: exact-int only or no user code across cached items.

# CPython Sanitizer Pattern Audit — audit4

Started: 2026-09-11
Auditor: Claude Code
CPython under test: `origin/main` @ `e5d4fa281c573b764b827f3defae260787024e43` (3.16.0a0)
Sanitizer build: docker image `taxoshop/cpython-asan-ubsan:current`
  - ASan + UBSan, gcc, `--without-pymalloc`, `PYTHONMALLOC=malloc`
  - interpreter: `/src/cpython/python`
  - ASAN_OPTIONS=detect_leaks=0:abort_on_error=1:symbolize=1
  - UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1
  - CONSTRAINT: DO NOT USE CTYPES.

## Method
1. Read macro_taxo pattern write-ups + tally_bugs.py clustering.
2. Highest-yield families (by cluster count):
   - workflow-0014 (38): retained pointer dereferences storage after owner releases.
   - workflow-0080 (22): callback re-entrancy invalidates borrowed state/backing storage.
   - workflow-0137 (20): reentrant argument conversion invalidates a backing resource.
3. Grep current source for capture-pointer/size -> user-code -> use-stale idioms:
   PyNumber_AsSsize_t, PyNumber_Index, _PyEval_SliceIndex, PyObject_GetBuffer,
   PyObject_IsTrue, PyObject_RichCompareBool, __index__/__buffer__/__eq__/__hash__ paths.
4. Confirm each candidate under the ASan/UBSan image with a minimal, ctypes-free repro.
5. Check open/closed CPython issues to avoid duplicates before write-up.

## Prior audits (avoid re-reporting)
- audit2 FINDING-001: mmap subscript-assign reentrant resize() (workflow-0137). CONFIRMED there.
- audit3: hz decoder OOB (dup), sqlite blob (safe/dup).
- Known massive sweep already fixed gh-142xxx..gh-154xxx across mmap, sqlite, struct,
  array, pickle, io, socket, memoryview, bytes.hex, csv/json. Treat those modules'
  obvious sites as likely-patched; verify before claiming.

## Candidate log  (IDEA / TESTING / CONFIRMED / DUP / FALSE)

### CONFIRMED — NEW
- **TextIOWrapper read path UAF via reentrant detach()** — CONFIRMED, believed NEW.
  `buffer_access_safe()` (textio.c:740) returns a *borrowed* `self->buffer`; the
  `buffer_callmethod_*` helpers call into it (read/readline/read(n)); the raw layer's
  `readinto()` (user code) can call `tw.detach()`, dropping the buffer's last ref and
  freeing the (C) BufferedReader while its `read_impl` is on the stack → heap-UAF WRITE
  at bufferedio.c:1022 / :1667. Parent pattern workflow-0137 (+0014).
  Repro: repro/textio_detach_uaf.py (+readline, +control). Logs: logs/textio_detach_*.
  Dup check: NOT #154997 (that = self->raw NULL-deref via buffered's own detach),
  NOT gh-153539/#157197-93 (tell snapshot), NOT #154523 (FT data race). → FINDING-001.
  Scope: read/readline/read(n) UAF; write no-crash; seek/tell/truncate guarded by the
  buffered reentrancy check (RuntimeError). Control (keep detached buf alive) => clean
  ValueError, isolating the defect to the missing strong ref across the outbound call.

### CONFIRMED — DUPLICATE (do not report)
- **mmap `__setitem__` reentrant resize OOB write** — CONFIRMED still crashes on
  e5d4fa28 (SEGV mmapmodule.c:406/1692, both integer-`__index__` and slice-`__buffer__`
  vectors). Already reported UPSTREAM as **#157335** (opened 2026-09-11, same repro).
  DUPLICATE — not reported. (Also the prior local audit2 FINDING-001.)
  Note: bytearray's identical slice-assign pattern was fixed (gh-153578); mmap missed.

### FALSE / SAFE (verified hardened — scoping evidence)
- bisect_right/insort — SAFE (sq_item re-checks bounds each iteration).
- deque count/contains/index/remove — SAFE (Py_NewRef + `state`-change guard, crit sec).
- json encoder dict/list/mapping — SAFE (gh-142831/145244: INCREF borrowed, re-read).
- bytearray find/index/count/startswith/endswith — SAFE (`ob_exports++` pins storage).
- bytearray setitem/ass_subscript/insert/setslice — SAFE (convert first; AS_STRING &
  size re-read after user code; gh-153578 re-clamps slice bounds after __buffer__).
- array setitem/ass_subscr/extend/frombytes/fromfile/imul — SAFE (CHECK_ARRAY_BOUNDS
  after conversion; slice only accepts array; frombytes/fromfile re-read state).
- heapq siftup/siftdown — SAFE (re-fetch _PyList_ITEMS + size-change guard).
- memoryview ass_sub (int/tuple/slice) — SAFE (pack_single CHECK_RELEASED_AGAIN after
  value conv; copy_single/getbuffer path detects release; exporter pinned via exports).
- struct pack_into / unpack_from — SAFE (dest buffer pinned by getbuffer for whole call).
- sqlite Blob subscript / ass_subscript (index & slice) — SAFE (sqlite3_blob_* NULL-check
  the closed handle -> ValueError; matches audit3).
- select.select seq2set — SAFE (Py_INCREF each obj before fileno(); size re-checked).
- _io Buffered seek/readinto/write — SAFE (fixed-size heap buffer; CHECK_CLOSED; no
  raw-ptr cached across user code in fast paths).
- csv writer.writerow — SAFE for memory (self->rec re-read fresh each join_append;
  reentrancy causes only logical/output corruption, not UAF).
- set &/|/-/^ and in-place + issubset with reentrant clearing __eq__ — SAFE.
- dict update/fromkeys, frozenset hash, str/bytes translate, str.format_map,
  codecs encode/decode error handlers, charmap_decode, pickle dump/load (running guard),
  sorted/min key mutation, int.from_bytes, bytes % b, list slice-assign — SAFE.
- float->int OOB (time.sleep/gmtime/localtime/ctime, datetime.fromtimestamp,
  select timeout, socket.settimeout) — SAFE (all raise OverflowError; no UBSan).
- mmap read subscript (int/slice), write, move, find/rfind — SAFE (bounds re-checked
  vs current size after conversion; clinic converts move/write args up front).
- elementtree Element subscript/ass_subscript (int & slice) — SAFE (gh-143200:
  re-validate length + fresh children[] in get/setitem; slicelen computed post-conv).
</content>
</invoke>

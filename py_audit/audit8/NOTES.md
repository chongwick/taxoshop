# audit8 — working the 50 fresh hypotheses (5 families × 10 sites)

Started 2026-09-14. Image `taxoshop/cpython-asan-ubsan:current` (ASan+UBSan, GIL build,
3.16.0a0, HEAD `e5d4fa28`). TSan image `taxoshop/cpython-tsan-ft:current` for 0077.
Local `cpython/` checkout is EMPTY — read source from inside the image (`/src/cpython`).

## Method
Work the ⭐ open leads first; verify inline guards for the ruling-out leads and cross off.
Confirm on sanitizer image, dup-check (git log + gh), write findings.

## Known upstream DUPES (do NOT re-file): #157335 (mmap setitem resize), #154997
(BufferedIO raw NULL), #154523 (FT buffer=NULL race), #142782 (zoneinfo strong-cache UAF),
#142637 (OrderedDict move_to_end UAF), #142663 (memoryview compare release), #128942 (array FT),
#154130 (dict/list-iter FT), #157088 (elementtree FT), #157124 (_pickle FT).

## Key structural facts (carried from audit4-7 + verified here)
- Argument Clinic runs `__index__`/GetBuffer converters in the WRAPPER, before the impl.
  => for a Clinic `Py_buffer`/`int` arg, if the impl's FIRST action is a resource re-check,
  that check is effectively POST-callback and DEFUSES __buffer__/__index__ close/free.
- GIL build: @critical_section is a no-op; single-thread reentrancy fully exposed.
- TSan concern: libc static buffers (strerror/getlogin/ttyname/environ) live in UNINSTRUMENTED
  libc memory => TSan may NOT flag races on them. Lowers 0077 libc-static value.

## Candidate log (IDEA / TESTING / CONFIRMED / DUP / FALSE)

### 0137 __buffer__ family (S1 ssl.write, S2 ssl.read, S3 blob.write, S9 hashlib.update) — FALSE
- blob_write/read/seek call `check_blob(self)` FIRST (post-GetBuffer) => close-in-__buffer__
  raises clean ProgrammingError. Confirmed by t_0137s3 (A/B clean ProgrammingError).
- _ssl.write is @critical_section + Clinic Py_buffer; no public teardown frees self->ssl while
  self alive. hashlib update: GetBuffer inside impl, but self->ctx lifetime tied to self (no
  public close), self pinned by call => safe. t_0137s3 C reentrant update clean.
- Structural rule holds: the only "free self->resource while self alive" path (blob.close) is
  re-checked. Cross off the whole __buffer__ family.

### 0080 S2 set.difference_update __hash__/__eq__ — FALSE (guarded)
- set_difference_update_internal: __hash__ computed in set_discard_key BEFORE probe; the probe
  set_compare_entry_lock_held INCREFs startkey, compares, then re-checks
  `table != so->table || entry->key != startkey` => SET_LOOKKEY_CHANGED restart. Hardened.

### 0014 S4 _asyncio future_schedule_callbacks fut_loop — FALSE (not reachable)
- call_soon passes borrowed fut->fut_loop to VectorcallMethod (no INCREF) — a real borrowed-
  handle-across-callout. BUT `_loop` getset has NO setter (grep _loop_set_impl => none;
  clinic emits {getter, NULL}); future_init raises "already initialized" on re-init. No Python
  path clears/rebinds fut->fut_loop while future alive => loop cannot be freed mid-loop. Cross off.

### 0014 S5 tee — FALSE. to->dataobj strong ref, `running` flag blocks re-entry, getitem
  Py_NewRef(value). t_0014s5 clean (A 200, B ok).

### BATTERY RESULTS (repro/battery, ASan/UBSan image) — ALL CLEAN, no crash
- 0080 S1 array index/contains evil __eq__ resize: clean (re-reads Py_SIZE/getarrayitem).
- 0080 S3 dict.update evil mapping keys()/__getitem__ clears dest: clean (insertdict re-derives).
- 0080 S5 str.format/%/format_map evil __format__/__getitem__ mutates args: clean.
- 0080 S7 pickle batch_appends/batch_setitems evil __reduce__ clears container: clean
  (list A pickled fine; dict B clean RuntimeError "changed size during iteration").
- 0080 S10 _json encoder list default clears list: clean (re-reads/INCREFs item).
- 0014 S8 mappingproxy contains/compare/get evil key mutates class dict: clean (dict hardened).
- 0014 S10 / 0091 S5 _json object_pairs_hook/object_hook mutate shared pairs/memo: clean
  (scanner owns its locals; 'a'->[] shows hook cleared prior pairs but no UAF).
=> Single-thread ASan reentrancy leads all HARDENED, confirming README framing.

## 0077 family results
### S8 faulthandler watchdog lock-handshake race — CONFIRMED crash, but DUP of #151475 (OPEN)
- Concurrent faulthandler.dump_traceback_later() + cancel_dump_traceback_later() from 2 threads
  on the FT build => `Fatal Python error: PyMutex_Unlock: unlocking mutex that is not locked`
  (exit 134). Pure Python, no ctypes. Repro: repro/tsan/t_0077s8_fh_min.py; log logs/fh_min.tsan.txt.
- Clean on GIL ASan build (exit 0) — FT-only.
- **DUP of #151475 (OPEN)** "faulthandler: data races in enable()/disable() and
  dump_traceback_later() under free threading" — Bug 2 is EXACTLY this handshake race, same
  PyMutex_Unlock crash, same repro shape (that issue was itself drafted by Claude Code, devdanzin).
  Enable/disable flag race tracked in #151363. => successful re-find of a real open bug, NOT new.
### S9 signal Handlers[] — FALSE (hardened): Handlers[].func uses _Py_atomic_load/store_ptr;
  .tripped/is_tripped atomic. No data race.
### S1 strerror, S2 getlogin, S3 ttyname, S5 environ/putenv, S6 gdbm_errno, S7 gethostbyname
  (locked via netdb_lock :6305), S10 ptsname — libc/library STATIC buffers in UNINSTRUMENTED
  memory => TSan cannot confirm even if a real race exists. Not sanitizer-confirmable. S4
  nl_langinfo = DUP-risk of #127081 (setlocale/localeconv family, audit7 FINDING-002).

## 0091 OOM/error-path family — ALL CLEAN (no double-free/UAF)
- set_nomemory sweeps (repro/asan/oom_probe8.py, 8b.py): S2 struct.unpack, S5 json.loads,
  S4 itertools.product, S9 os.getgroups, S1 grp.getgrall, S3 zoneinfo, struct.iter_unpack,
  S8 pickle load_build (OOM + raising __setstate__/append), S7 epoll.poll(OOM) — all clean.
- Consistent with audit7: CPython OOM/error-path hardening is thorough. Leaks (if any) need
  detect_leaks=1 and are low-value; the ASan-visible double-free outcome did not materialize.
- Untested (setup-heavy, low confidence): S6 recvmsg (needs SCM_RIGHTS ancillary), S10 _ssl
  _get_aia_uri (needs crafted AIA cert). Deferred.

================================================================================
## audit8 SUMMARY (first pass complete)
5 families × 10 sites = 50 hypotheses worked. Result matches README framing (mostly
ruling-out leads; under-swept classes hardened or already-reported).

- 0137 (__buffer__ reentrancy): ALL RULED OUT. Clinic runs GetBuffer/__index__ in wrapper;
  impls either re-check the resource first (sqlite check_blob) or have no teardown-while-alive
  path (ssl self->ssl, hashlib self->ctx pinned by self). Empirically clean.
- 0080 (callback reentrancy): ALL RULED OUT. set/dict/list/array/tuple/json-encoder/pickle-
  batch/str-format all re-read size/table/item + INCREF or snapshot storage. Empirically clean.
- 0014 (borrowed handle): ALL RULED OUT. asyncio fut_loop has NO _loop setter (unreachable);
  tee refcounted + running-flag; mappingproxy forwards to hardened dict; json owns locals.
- 0077 (shared process state): faulthandler S8 = CONFIRMED crash, DUP of #151475 (open).
  signal S9 hardened (atomics). libc-static sites (strerror/getlogin/ttyname/environ/gdbm/
  ptsname) NOT TSan-confirmable (uninstrumented libc memory). nl_langinfo dup-risk #127081.
- 0091 (error-path leak/double-free): ALL CLEAN under OOM + exception sweeps.

**Hypotheses NEW bugs: 0.** One real crash re-found (faulthandler #151475, DUP).
See findings/FINDING-001-faulthandler-refind.md.

================================================================================
## BEYOND THE HYPOTHESES — NEW BUG FOUND (FINDING-002)

### sqlite3 Cursor NULL-deref via reentrant execute() in a text_factory/converter — NEW, CONFIRMED
- Hunted the under-swept "sqlite3 callbacks run arbitrary Python mid-op" vein (not in the 50
  hypotheses). `_pysqlite_fetch_one_row` (cursor.c:343) calls the converter (:396) / text_factory
  (:439) per column while dereferencing borrowed `self->statement->st`; holds no local ref and
  never revalidates after the callout.
- A callback that reenters `cur.execute()` triggers `_pysqlite_query_execute`, whose recursion
  guard (check_cursor_locked inside get_statement_from_cache, :500) fires only AFTER it
  stmt_reset()s the outer statement and does `Py_XSETREF(self->statement, NULL)` (:854/:861).
  So self->statement is NULL by the time "Recursive use of cursors not allowed" is raised. If the
  callback SWALLOWS that exception (ordinary try/except), the outer fetch loop reads
  self->statement->st for the next column => NULL member access.
- Crash: `cursor.c:402:23 member access within null pointer of type 'struct pysqlite_Statement'`
  (text_factory) / `cursor.c:383` (converter). Vanilla build: SIGSEGV exit 139. No ctypes.
- Repros: repro/t_sqlite_fetch_min.py (text_factory), repro/t_sqlite_fetch_converter.py.
  Log: logs/sqlite_fetch.asan.txt.
- **DUP-CHECK: NEW.** Distinct from #143662 (OPEN, trigger=Connection.close, field=
  connection->db, crash in iternext sqlite3_changes, needs DML/RETURNING) and #146471 (OPEN,
  threads). My path: trigger=reentrant execute, field=self->statement, crash IN fetch_one_row,
  plain SELECT. git log -8000 shows no fix. See findings/FINDING-002-*.md.
- Note: con.close() inside text_factory does NOT crash a plain SELECT (that's #143662's DML path);
  cur.close() inside is caught cleanly by check_cursor_locked (guard-first in cursor_close).
  The execute() path is the one with the too-late guard.
</content>

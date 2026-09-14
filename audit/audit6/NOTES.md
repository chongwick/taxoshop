# audit6 — Hypotheses re-confirmation run

Started 2026-09-12. Goal: work the 60 hypotheses in `Hypotheses/` (6 families × 10 sites).
Confirm the real ones ("refind" the already-confirmed). Image
`taxoshop/cpython-asan-ubsan:current` (ASan+UBSan, GIL build, HEAD `e5d4fa28`, 3.16.0a0);
TSan image `taxoshop-cpython-tsan:latest` for 0077/0081. Local cpython checkout `7bfa97f4`.

## Calibration (carried from audit5)
- GIL build => `@critical_section` is a no-op: single-thread reentrancy (0014/0080/0137)
  fully exposed here.
- 0077/0081 are concurrency: need TSan image.
- 0091 leaks: ASan runs detect_leaks=0 -> use `sys.gettotalrefcount()` deltas or
  detect_leaks=1.
- UBSan (GCC) does NOT catch float-cast-overflow (0010) or null+0 memcpy (0005).

## Known upstream DUPES (do NOT re-file as new): #157335, #154997, #154523,
audit4/audit5 findings.

## Candidate log (IDEA / TESTING / CONFIRMED / DUP-UPSTREAM / FALSE)

### wf0080 Site 1 — zoneinfo strong-cache find_in_strong_cache  ✅ CONFIRMED
- **CONFIRMED heap-UAF**, ASan crash at `Modules/_zoneinfo.c:2449 in find_in_strong_cache`
  (`node = node->next`), reached via `zone_from_strong_cache:2526` <-
  `zoneinfo_ZoneInfo_impl:319`. Freed by `strong_cache_node_free:2382` <-
  `clear_strong_cache:2588` <- `zoneinfo_ZoneInfo_clear_cache_impl:523`.
- Repro: repro/wf0080_s1_zoneinfo.py (str subclass whose __eq__ calls ZoneInfo.clear_cache()).
  Log: logs/wf0080_s1_zoneinfo.asan.txt.
- **Already reported upstream: #142782 (OPEN)** — "Use-after-free in zone_from_strong_cache
  via re-entrant ZoneInfo.clear_cache() from key __eq__". This is the taxonomy's evidence
  issue; still unfixed on HEAD. NOT distinct from #142782 => not a NEW finding, but a
  successful re-find of a confirmed real bug.
- Note gh-142783 (weak_cache refcount) is a DIFFERENT UAF; does not cover this path.

### wf0080 Site 7 — OrderedDict move_to_end under key __eq__  ✅ CONFIRMED
- **CONFIRMED heap-UAF**, ASan crash at `Objects/odictobject.c:549 _odict_get_index_raw`
  <- `_odict_get_index:614` <- `_odict_find_node:645` <- `OrderedDict_move_to_end_impl:1351`.
  Freed by `clear_lock_held`(dict) <- `OrderedDict_clear_impl:1225`, triggered from evil
  key `__eq__`->`od.clear()` during `_Py_dict_lookup`/`compare_generic`.
- Repro: repro/battery/t_wf0080_s7_ordereddict.py. Log: logs/wf0080_s7_ordereddict.asan.txt.
- **Already reported upstream: #142637 (OPEN)** — "Use-after-free in several OrderedDict
  operations via re-entrant __eq__", explicitly names move_to_end/pop. gh-148660 fixed only
  copy(); move_to_end path still crashes. Re-find of confirmed real bug.

### Clean so far (single-thread, no crash):
- wf0080 S3 elementtree find(): find() returned None, no crash (path likely snapshots).
- wf0080 S8 functools.reduce: clean (args slots owned across call).
- wf0080 S9 cProfile evil timer: clean.
- wf0137 S3 sre match[EvilIndex]: clean (match holds owned string ref).
- wf0137 S10 array ass_subscript EvilIndex del arr[:]: clean (re-reads ob_item/size).
- wf0137 S2 mmap slice __setitem__ resize(0) in __index__: clean (bounds re-checked; item
  path #157335 is the known dup, slice path not crashing here).
- wf0014 S1 interpchannels: recv memoryview after destroy(sender)+gc -> clean (buffer
  copied/pinned; distinct from audit5 OOM double-release finding).
- wf0014 S2 SharedMemory.buf after close(): ValueError "released memoryview" -> hardened.
- wf0014 S6 contextvars Context.run reentrant enter: clean.
- wf0014 S7 pyexpat subparser after parent del: clean (child holds parent state safely).
- wf0080 S3b elementtree findall evil tag __eq__ clear(): clean (re-reads child count).
- wf0081 S2b decimal reentrant __bool__ (my crafting) clean — but real #155493 is OPEN
  (needs precise last-ref-in-container path; not reproduced this session).

### wf0080 Site 7 CONFIRMED (2nd path) — OrderedDict.pop()
- t_wf0080_s7b_odict_pop.py -> same crash `odictobject.c:549 _odict_get_index_raw`.
  Matches OPEN #154817. Log logs/wf0080_s7b_odict_pop.asan.txt.

## Concurrency families (wf0077, wf0081) — TESTED on new free-threaded TSan build
Built `taxoshop/cpython-tsan-ft:current` = free-threaded (`Py_GIL_DISABLED=1`) + TSan,
HEAD e5d4fa28, via reconfiguring the asan image in a container (Dockerfile also updated with
a `tsan-ft` stage; the direct `docker build` hit an apt-GPG cache error, env issue).
Run with `-e PYTHONMALLOC= -e TSAN_OPTIONS=halt_on_error=1:history_size=7`.
Caveat: `_decimal`/`_zstd` C modules did NOT build (missing libmpdec etc) — `import decimal`
falls back to pure-Python `_pydecimal`, so wf0081 S2 decimal (#149142) NOT validly tested.

### CONFIRMED TSan races (all re-finds of OPEN upstream issues):
- **wf0081 S10 array**  ✅  append `i_setitem` arraymodule.c:398 (write) vs `tobytes`
  array_array_tobytes_impl:1934 memcpy (read) on `ob_item`, no lock. = **#128942 OPEN**
  ("array not free-thread safe"; fix gh-128943 REVERTED by #130707 for perf). [FINDING-003]
  Log logs/wf0081_s10_array.tsan.txt (8 races).
- **wf0081 S6 dict iterator**  ✅  shared iterator cursor: write `dictiter_iternext_threadsafe`
  dictobject.c:6158 vs read `dictiter_iternextkey`:5784. = **#154130 OPEN** (double-DECREF
  di_dict). [FINDING-004] Log logs/wf0081_s6_dict_iter.tsan.txt.
- **wf0077 S3/S9 subinterp init**  ✅  write-write on shared static exc type
  `exc->tp_vectorcall` `_PyExc_InitTypes` exceptions.c:4566 during concurrent `I.create()`.
  = **#129824 OPEN** (subinterp TSAN races). [FINDING-005] Log logs/wf0077_s3_subinterp.tsan.txt.

### Clean (0 TSan races) this run — likely locked/serialized on FT build:
- wf0081 S1 hashlib, S3 bytearray, S4 bz2, S5 list.sort, S6b list iter, S7 ctxvars iter,
  S8 BufferedWriter, S9 mmap.  wf0077 S1 setlocale, S2 random, S4 warnings, S6 tracemalloc,
  S8 environ.  (S2 decimal untestable, see above.)
- NOTE: wf0081 S7 ctxvars-iter clean here but #154535 (Context HAMT iter cross-thread) is
  OPEN — my schedule may not have hit it; worth a sharper repro. list.sort (#154756) &
  bytearray (#130977) also clean — either fixed or need a tighter window.

## OLD tsan image (`taxoshop-cpython-tsan:latest`) = GIL-enabled (Py_GIL_DISABLED=0),
useless for these families. Superseded by taxoshop/cpython-tsan-ft:current.

## Leak family (wf0091) — NOT productively testable this session
- Release build: no `sys.gettotalrefcount`; ASAN_OPTIONS baked detect_leaks=0. Would need
  LSan override (noisy). Strongest lead (S3 zoneinfo load_data) already fixed by gh-156067.

## SESSION OUTCOME
Re-found 5 confirmed bugs (all OPEN upstream, unfixed on HEAD) across the hypotheses:
ASan single-thread (GIL image):
1. wf0080 S1 zoneinfo find_in_strong_cache  -> #142782 (OPEN)  [FINDING-001]
2. wf0080 S7 OrderedDict move_to_end + pop   -> #142637 / #154817 (OPEN)  [FINDING-002]
TSan free-threaded (new taxoshop/cpython-tsan-ft:current image):
3. wf0081 S10 array append-vs-tobytes race   -> #128942 (OPEN)  [FINDING-003]
4. wf0081 S6 shared dict-iterator cursor race -> #154130 (OPEN)  [FINDING-004]
5. wf0077 S3/S9 subinterp _PyExc_InitTypes race -> #129824 (OPEN)  [FINDING-005]
No NEW (previously-unreported) bug found; all five are the taxonomy's evidence sites and
confirm the hypotheses are live/unfixed. Leak family (wf0091, 10 sites) still untested
(no refcount build). Best next: sharper repros for #154535 (ctxvars iter), #154756
(list.sort), decimal with _decimal C module built (libmpdec).
</content>

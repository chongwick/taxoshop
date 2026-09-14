# Hypotheses (audit7) — fresh candidate sites for workflow-0014 / 0080 / 0091 / 0077

A **new** set of hunting hypotheses (not confirmed bugs), generated after audit6/audit7. These
are **distinct** from the original root `Hypotheses/` set and from the already-confirmed/known
findings (zoneinfo strong-cache #142782, OrderedDict #142637, array #128942, dict-iter #154130,
subinterp init #129824, elementtree #157088, itertools FT sprint #123471/#151409). 10 sites per
family, each with a real `file:line` anchor in the checkout (HEAD `7bfa97f4`).

| File | Family | Mechanism |
|------|--------|-----------|
| [workflow-0014.md](workflow-0014.md) | Borrowed/derived handle used after owner/backing invalidation | stale pointer / cache / derived view / teardown / error-path decref-then-use |
| [workflow-0080.md](workflow-0080.md) | Callback re-entrancy invalidates borrowed state | hash / eq / str / iter callback mutates the active object mid-op |
| [workflow-0091.md](workflow-0091.md) | Error-path ownership loss (leak of an owned intermediate) | owned temp built before a fallible step; error exit skips release |
| [workflow-0077.md](workflow-0077.md) | Concurrent contexts race on shared process-wide state | libc static buffers / module globals / lazy caches / one-time init (TSan) |

## Calibration carried in
- ASan/UBSan image `taxoshop/cpython-asan-ubsan:current` (GIL build): single-thread reentrancy
  (0014/0080) fully exposed; `@critical_section` is a no-op there.
- Free-threaded TSan image `taxoshop/cpython-tsan-ft:current` (`Py_GIL_DISABLED=1`): needed for
  0077 races. Run with `-e PYTHONMALLOC= -e TSAN_OPTIONS=halt_on_error=1:history_size=7`.
- 0091 leaks: release build has no `sys.gettotalrefcount`; detect via `detect_leaks=1` LSan
  override or repeated-call RSS/`tracemalloc` deltas. A double-free/UAF on the error path (not a
  mere leak) is the higher-value outcome and is ASan-visible.
- **Policy note (important):** free-threaded C-extension one-off crashes are being consolidated
  upstream and several were closed `not_planned` (see audit7 NOTES, #157088/#157124). Weight
  0077 sites by whether they are a *distinct* shared-state class, not just "share object across
  threads."
- No `ctypes` in any reproducer.

## Site writeup structure
Site (`file:line`, function, the handle/temp/field) · Reasoning · Why it fits · Reachability
(Python entry point) · Trigger hypothesis · Confidence & dup-check.

---

## RESULTS (relentless re-find run, 2026-09-14)
Repros in `repro/asan/hyp/` (single-thread, ASan/UBSan image) and `repro/tsan/hyp/`
(free-threaded TSan image). Logs in `logs/`.

**0014 (borrowed handle) — ALL HARDENED.** Tested S1,S2,S3,S4,S5,S7,S8,S9,S10.
- S1 `memoryview.index` release: guarded — `memory_item` re-checks `CHECK_RELEASED`.
- S4 dict-view compare: `all_contained_in` uses a dict iterator → "dict changed size" RuntimeError.
- S2 partial (pinned by tp_call), S3 DirEntry (caches own path), S5 sqlite Row (owns own
  `description` ref), S8 generator ("already executing"), S9 super (owns refs), S10 RWPair
  (owns reader/writer). None crash under ASan.

**0080 (callback reentrancy) — ALL HARDENED.** Tested S1,S3,S4,S5,S8,S9 + read-verified
S2/S6/S7/S10. `dict_equal` INCREFs + re-derives each step; `set_add_entry_takeref` re-reads
`so->table` via `restart:`; deque iterator checks `state`; `lru_cache` re-fetches the link
*after* the `__hash__` callout; Counter/json re-lookup / snapshot. No crash.
(Gotcha: use **distinct-but-equal** evil objects — identical objects make `RichCompareBool`
short-circuit on pointer identity and `__eq__` never fires.)

**0091 (error-path leak/UAF) — ALL CLEAN.** `oom_hyp.py` swept `set_nomemory(k,k+1)` k=0..59
for all 10 targets (getnameinfo, time/date.fromisoformat, pickle save_reduce 6-tuple,
csv.writerow, getgrouplist, sched_getaffinity, groupby ctor, ET deepcopy, json default
circular). No double-free/UAF/abort.

**0077 (concurrency / TSan) — 2 CONFIRMED, others fixed/known/clean:**
- **S2 localeconv/setlocale — CONFIRMED (69 races).** DUP of open #127081. → FINDING-002.
- **S1 tzset — CONFIRMED (6 races), concurrent `time.tzset()`.** Not in #127081/#149816;
  under-tracked. → FINDING-003.
- S6 getservbyname/getprotobyname — CLEAN: **already fixed** (reentrant `_r`, PR #132750 under
  #127081). A real bug the hypothesis correctly named, now closed.
- S7 localtime/gmtime — CLEAN: localtime_r/gmtime_r used.
- S3 syslog — CLEAN: `@critical_section` on openlog/syslog/closelog + defensive INCREF of
  `S_ident_o` across the ALLOW_THREADS window.
- S4/S5/S9 subinterp one-time init (extensions cache / datetime / json) — every target collapses
  to the SAME race: `_PyExc_InitTypes` `exc->tp_vectorcall=` (`exceptions.c:4566`) = **DUP of
  #129824** (subinterp type init), not a module-specific init bug. S8 readline / S10 curses
  not tested (niche; need built extension / tty).

**Bottom line:** the single-thread families (0014/0080) and the OOM family (0091) are swept clean
here. The productive family is 0077: its hypotheses landed on *real* thread-unsafe process-global
state — one tracked-open (localeconv/setlocale #127081), one apparently untracked (tzset), one
already-fixed (getserv). No brand-new *reportable* bug, but the "confirmed to exist" races were
found and TSan-verified.
</content>

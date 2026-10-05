# Hypotheses (audit8) — 50 fresh candidate sites for the top-5 macro-taxonomy families

A **new** set of hunting hypotheses (candidate sites, *not* confirmed bugs), generated for the
top-5 highest-yield families from `tally_bugs.py`. 10 sites per family (50 total). Every site
carries a real `file:line` anchor in the checkout baked into
`taxoshop/cpython-asan-ubsan:current` — CPython HEAD **`e5d4fa28`** (3.16.0a0).

These are **distinct** from the audit7 `Hypotheses/` set, from the confirmed/known findings
(textio-detach #154997, mmap-resize #157335, zoneinfo #142782, OrderedDict #142637, array
#128942, dict-iter #154130, subinterp-init #129824, elementtree #157088, locale/setlocale
#127081, tzset), and from the OOM-swept builder list in `audit7/NOTES.md`.

## Top-5 families targeted (rank / count / summary)

| # | Family | File | Count | Mechanism |
|---|--------|------|-------|-----------|
| 1 | workflow-0014 | [workflow-0014.md](workflow-0014.md) | 38 | Borrowed/derived handle used after owner/backing invalidation |
| 2 | workflow-0080 | [workflow-0080.md](workflow-0080.md) | 22 | Callback re-entrancy invalidates borrowed state/backing storage |
| 3 | workflow-0137 | [workflow-0137.md](workflow-0137.md) | 20 | Reentrant argument conversion invalidates a backing resource |
| 4 | workflow-0077 | [workflow-0077.md](workflow-0077.md) | 11 | Concurrent contexts race on shared process-wide state (TSan) |
| 5 | workflow-0091 | [workflow-0091.md](workflow-0091.md) | 10 | Error-path ownership loss (leak/UAF of an owned intermediate) |

## Reality check (read before hunting)

audit4–audit7 established that CPython's obvious single-thread reentrancy loops are **already
hardened**: sequence search/compare loops re-read `Py_SIZE` and re-derive the item pointer per
iteration and `Py_NewRef` each item before the callout (verified here for `array.index`,
`deque.count`, `list_richcompare`, `bytearray.extend`, `select.seq2set`, `_asyncio`
callback list). Argument Clinic also runs `__index__`/`GetBuffer` conversions in the *wrapper*,
**before** the impl captures native state, which structurally defuses many classic 0137 sites.

Consequently a large fraction of the sites below are honest **ruling-out leads** (guard is
identified inline — verify it, then cross the site off). The genuinely-open leads are flagged
⭐ and clustered around three under-swept classes:

1. **PEP-688 `__buffer__` reentrancy** (0137/0080): `PyObject_GetBuffer(arg)` now runs
   arbitrary Python (`arg.__buffer__`) which can free a *different* `self->resource` that
   Argument Clinic cannot protect (`_ssl`, `_sqlite3.Blob`, `_hashlib`).
2. **Borrowed non-container handles** (0014): `fut->fut_loop`, tee-data links, dialect objects —
   fields the hardened "re-read size / NewRef item" pattern does not cover.
3. **libc static-buffer / true-global races** (0077): `strerror`, `getlogin`, `ttyname`,
   `environ`, `gdbm_errno`, faulthandler/signal globals — distinct shared-state classes from
   audit7's `tzname`/`localeconv`/`getserv`/`localtime`.

## Calibration carried in
- ASan/UBSan GIL image `taxoshop/cpython-asan-ubsan:current`: single-thread reentrancy
  (0014/0080/0137) fully exposed; `@critical_section` is a no-op there.
- Free-threaded TSan image `taxoshop/cpython-tsan-ft:current` (`Py_GIL_DISABLED=1`): needed for
  the 0077 races. Run with `-e PYTHONMALLOC= -e TSAN_OPTIONS=halt_on_error=1:history_size=7`.
- 0091 leaks: release build has no `sys.gettotalrefcount`; use `ASAN_OPTIONS=detect_leaks=1`
  (LSan) or repeated-call RSS/`tracemalloc` deltas. A double-free/UAF on the error path (not a
  mere leak) is the higher-value, ASan-visible outcome. Force failures with
  `_testcapi.set_nomemory(k, k+1)` — **no `ctypes`** in any reproducer.
- **Policy note:** free-threaded C-extension one-off crashes from sharing an object across
  threads are being consolidated upstream and several closed `not_planned` (audit7 NOTES,
  #157088/#157124). The 0077 sites here deliberately target *distinct shared-state classes*
  (libc statics / true process globals), not "share one object across threads."

## Site writeup structure
Site (`file:line`, function, the handle/temp/field) · Reasoning · Why it fits · Reachability
(Python entry point) · Trigger hypothesis · Confidence & dup-check.
</content>

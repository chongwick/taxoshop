# CPython Sanitizer Bug Hunt — Summary Log

- Target: CPython `f5394c257ce` (3.15.0a1), built with ASAN+UBSAN (see Dockerfile).
- Harness: persistent container `cpy`, source at `/src/cpython`, repros under `findings/repros`, sanitizer logs under `findings/logs`.
- Guiding taxonomies: `taxos/macro_taxo/*` (mechanism-first), `taxos/micro_taxo/*` (known issues to avoid duplicating).

## Baseline
- [x] Known repro `repro/issue_143545.py` (lsprof re-entrant `__index__` UAF) confirmed: ASAN `heap-use-after-free` at `Modules/_lsprof.c:324`.

## Candidates investigated

| # | Area | Macro pattern | Status | Sanitizer result |
|---|------|---------------|--------|------------------|
| 1 | `_heapq` siftup/siftdown | reentrant compare | safe | guarded: re-checks size + reloads `_PyList_ITEMS` after each compare |
| 2 | `array` richcompare/index | reentrant compare | n/a | items are numeric/char only — comparisons don't re-enter Python |
| 3 | `mmap` ass_subscript | reentrant `__index__` | not-ASAN-visible | buffer is real `mmap()` memory, not ASAN-instrumented |
| 4 | `collections.deque` count/contains/index | reentrant compare | safe | guarded by `deque->state` counter checked after each compare |
| 5 | `bytearray` setitem/ass_subscript | reentrant `__index__` | safe | hardened by GH-91153 (convert value before size check, re-read size) |
| 6 | `bisect` insort/bisect | reentrant compare/key | safe | uses owned refs (`sq_item` new ref) + bounds-checked access |
| 7 | **`_json` encoder** `encoder_listencode_obj` | **reentrant callback / borrowed ref** | **CONFIRMED UAF** | **heap-use-after-free, `Modules/_json.c:1663`** |
| 8 | `_json` dict/mapping encoder loops | reentrant callback / borrowed ref | CONFIRMED UAF (variant) | heap-use-after-free, `Modules/_json.c:1741` (freed key via `%R`) |
| 9 | `_lsprof` root cause (POF_EXT_TIMER cleared before timer-return conversion) | reentrant callback | known (#143545) | `clear()` triggers (baseline); `disable()` guarded by `POF_ENABLED` check so no novel variant |
| 10 | `_elementtree` find/findtext/findall loops | reentrant compare | safe | `Py_INCREF(item)` before compare + re-read `children`/`length` each iter |
| 11 | `select.select` seq2set | reentrant `fileno()` | safe | explicit `Py_INCREF(o)` before `PyObject_AsFileDescriptor` |
| 12 | sweep: csv/join/reduce/heapq/bytes/dict.update/array.extend/list.extend | reentrant callback | safe | all hardened; no sanitizer hit |
| 13 | grep: other `#ifdef Py_GIL_DISABLED`+INCREF sites | borrowed ref (FT regression) | n/a | only `_json` has the pattern — Finding-01 is well-scoped |
| 14 | `functools.lru_cache` (bounded/infinite) | reentrant `__eq__` | safe | meticulously hardened (deferred decrefs, documented reentrancy handling) |
| 15 | `itertools` groupby/accumulate/dropwhile | reentrant callback | safe | empirical probes clean (`sweep2_*`) |
| 16 | `_ctypes` Array_ass_item / ass_subscript | reentrant `__index__` | (known area) | `ptr` computed before `PyCData_set`; overlaps known #143005 (`__class__` swap) |
| 17 | `_sqlite3` cursor converter lookup | borrowed dict ref | safe | borrowed converter INCREF'd immediately via `PyList_Append`, no callback between |
| 18 | `_elementtree`/`_sqlite`/`_pickle` borrowed `PyDict_GetItemWithError` | borrowed dict ref | safe | each wraps in `Py_XNewRef` or uses value before any callback |
| 19 | codec error handlers (decode/encode, ~16 encodings) | bounds/representation | safe | crafted positions/replacements bounds-checked (`cod_*` probes clean) |
| 20 | `dict_equal` value comparison | reentrant `__eq__` | safe | INCREFs key/aval/bval before compare; re-reads `ma_keys` each iter |
| 21 | UBSan sweep: datetime/math/int/struct/itertools/float extremes | bounds/representation / UB | safe | no UBSan hit; one ASAN allocator-cap artifact on absurd `to_bytes` (not a bug) |

## State of the hunt

The CPython core and most stdlib C accelerators are very thoroughly hardened
against the re-entrant-callback / borrowed-reference pattern (consistent
`Py_INCREF`-before-callback, size/state re-checks, `_lock_held` critical sections,
`list_get_item_ref` owned accessors). The confirmed `_json` encoder UAF slipped
through specifically because its protective `Py_INCREF` is compiled only under
`#ifdef Py_GIL_DISABLED` (gh-119438) — a **default (GIL) build regression**. A
grep confirmed that exact idiom exists **only** in `_json.c`, so the finding is
self-contained and its fix (unconditional INCREF in the three encoder loops)
fully closes it.

## Confirmed findings
- **[FINDING-01](FINDING-01-json-encoder-uaf.md)** — heap-use-after-free in `_json`
  encoder: borrowed list element used across the `default()` callback (with
  `check_circular=False`), freed access via `_PyErr_FormatNote("%T", obj)` at
  `Modules/_json.c:1663`. Repro: `repros/json_default_uaf.py`. Log:
  `logs/json_default_uaf.asan.txt`. Distinct from decoder bug #143544.

## Notes
- Method: for each candidate, form a hypothesis from a macro taxo, write a minimal repro, run under the ASAN/UBSAN `./python`, capture full sanitizer output to `findings/logs/`.

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
| 22 | **`OrderedDict.move_to_end`** | **reentrant `__eq__` clears owner** | **CONFIRMED UAF** | **heap-use-after-free, `Objects/odictobject.c:550`** (`_odict_get_index_raw` pre-lookup `ma_keys` snapshot) |
| 23 | `OrderedDict.pop` / `__delitem__` | reentrant `__eq__` clears owner | CONFIRMED (known #142637 path) | same site `:550` via `_odict_popkey_hash`; pins shared root cause |
| 24 | `OrderedDict.setdefault` | reentrant `__eq__` clears owner | safe | found-path INCREFs immediately; not-found path re-inserts without stale alias |
| 25 | `OrderedDict.__eq__` (`_odict_keys_equal`) | reentrant `__eq__` | safe | re-checks `od_state` after each compare → RuntimeError |
| 26 | `_collections.deque` index/count/remove/contains | reentrant `__eq__` | safe | `start_state != deque->state` re-checked after each compare |
| 27 | `_collections._count_elements` (`Counter.update`) | borrowed `oldval` across `__add__` | safe | uses owned `key` + owned `newval`; `oldval` only fed to `PyNumber_Add` |
| 28 | `list` index/count/remove/contains | reentrant `__eq__` | safe | `list_get_item_ref` owned accessor / re-read `ob_item[i]` under fresh `Py_SIZE` each iter |
| 29 | `memoryview` setitem (`pack_single`) | reentrant `__index__`/`__float__`/`__bool__` | safe | `CHECK_RELEASED_INT_AGAIN` re-check after every value conversion, before the write |
| 30 | `memoryview.tolist` (`tolist_base`) | reentrant unpack | n/a | `adjust_fmt` restricts to single native formats → no struct-module callback |
| 31 | `struct.Struct.pack_into` | reentrant value conversion frees buffer | safe | `PyObject_GetBuffer` pins exporter (blocks resize/release during `__index__`) |
| 32 | `set`/`frozenset` intersection/difference_update/symmetric_difference/isdisjoint | reentrant `__eq__` mutates the iterated set | safe (corpus GAP but hardened) | empirically clean: `__eq__` fired ~989×/op while clearing+refilling the iterated heap table; `set_next` re-reads `so->table`/`mask` each call + keys `Py_INCREF`'d. Probe: `probes/set_reentrancy3.py` |
| 33 | `_pickle` batch_list/batch_dict/batch_list_exact `_PyErr_FormatNote` | borrowed item/key across `save()` callback | safe | error-note formats the *container* (alive) or `Py_INCREF`s the item + re-checks `PyList_GET_SIZE` each iter |
| 34 | error-note sweep: `dictobject.c:3789`, `typeobject.c:11942` `_PyErr_FormatNote` | borrowed obj across callback | safe | dict one formats only an int index; type one iterates a private `PyDict_Copy` not reachable by user code |
| 35 | heapq heappushpop/heapreplace, max/min-key, dict.update(evil mapping), json object_pairs_hook, sorted-key, list-repeat `__index__` | reentrant callback mutates owner | safe | all guarded (heap raises RuntimeError/IndexError; owned refs elsewhere) |
| 36 | `_elementtree` Element.remove / find / findtext | reentrant `__eq__` on child tag | safe | re-checks `self->extra`/`length` and re-reads `children` each iter (explicit hardening comment) |
| 37 | **`ctypes.resize()` of a CData object with a live exported `memoryview`** | **lifetime / buffer-export ownership** | **CONFIRMED UAF** | **heap-use-after-free, freed at `_ctypes/callproc.c:1923` (`_ctypes_resize_impl`), read at `memoryobject.c:1063` (`PyBuffer_ToContiguous`)** |

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
## Dedup audit (by sanitizer crash location / stack trace, 2026-09-02)

**Methodology:** a finding is a duplicate iff its sanitizer crash location — the `#0`/faulting
application frame (`SUMMARY: AddressSanitizer: <class> <file:line> in <func>`) — matches the crash
location recorded in a known issue's Full Sanitizer Output. Issue title/component are *not* used;
different caller paths that fault at the same frame are the same bug.

| Finding | Crash location (`#0` / distinguishing app frame) | Corpus match? | Verdict |
|---------|--------------------------------------------------|---------------|---------|
| FINDING-01 list/`default()` | `_Py_TYPE object.h:277` → `_PyErr_FormatNote errors.c:1259` → **`encoder_listencode_obj _json.c:1663`** | none — 0 corpus stack frames reach any `_json.c` line | **NOT a duplicate** |
| FINDING-01 dict variant | **`encoder_encode_key_value _json.c:1741`** → `_encoder_iterate_dict_lock_held _json.c:1801` | none | **NOT a duplicate** |
| FINDING-02 `move_to_end` | **`_odict_get_index_raw odictobject.c:550`** | **gh_142637** = identical `SUMMARY … odictobject.c:550 in _odict_get_index_raw` | **DUPLICATE** — retracted |

Notes on the json-adjacent corpus entries (why they are *not* crash-location matches): `gh_143544`
(decoder UAF) records no symbolized stack; `gh_142831` / `gh_140750` / `gh_143196` are a different
bug class — heap-buffer-**overflow** at `0x5020000051a0` (indentation-cache `__mul__`), not this UAF.
FINDING-02 is a dup of `gh_142637` specifically (`:550`), *not* `gh_142734` (`:1276`,
`OrderedDict_copy_impl`).

Also confirmed KNOWN by crash-location where corpus has full stacks: array `__index__`
(**gh_144128**, `II_setitem`/`_PyNumber_Index` frames), OrderedDict.copy (**gh_142734**, `:1276`).

## Confirmed novel findings (post stack-trace dedup)
- **[FINDING-01](FINDING-01-json-encoder-uaf.md)** — `_json` encoder UAF. Both the list/`default()`
  frame (`_json.c:1663`) and the dict frame (`_json.c:1741`) are unmatched by any recorded corpus
  stack trace → novel.
- **[FINDING-03](FINDING-03-ctypes-resize-exported-buffer-uaf.md)** — `ctypes.resize()` frees a
  CData buffer still exported to a `memoryview` (no `bf_releasebuffer`/export accounting on CData;
  `_ctypes_resize` skips the export check). Crash: freed at `_ctypes/callproc.c:1923`, read at
  `memoryobject.c:1063` (`memoryview.tobytes`). Distinct crash location from `gh_113576` (threaded
  `CreateSwappedType` race), `gh_154524` (TSan race), `gh_143005` (buffer-overflow), `gh_143375`
  (SEGV null-deref, shares only the read frame). Repro: `repros/ctypes_resize_uaf.py`, log:
  `logs/ctypes_resize_uaf.asan.txt`.

## Retracted (duplicate by crash location)
- ~~FINDING-02 OrderedDict `move_to_end`~~ — crash frame `_odict_get_index_raw odictobject.c:550`
  matches **gh_142637** exactly. File kept as audit trail with a DUPLICATE banner; repro/log remain
  valid evidence of the *known* bug. Repro: `repros/od_move_to_end_uaf.py`, log:
  `logs/od_move_to_end_uaf.asan.txt`.

## Notes
- Method: for each candidate, form a hypothesis from a macro taxo, write a minimal repro, run under the ASAN/UBSAN `./python`, capture full sanitizer output to `findings/logs/`.

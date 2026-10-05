# php_audit1 — Validation NOTES

Validation of the 50 hypotheses in `Hypotheses.md` against a real PHP ASan/UBSan build.
Sibling of [[cpython-sanitizer-audit]] / [[cruby-sanitizer-audit]] work.

## Result (2026-09-16)

**No new memory-safety or leak bug confirmed.** PHP 8.6.0-dev's core is systematically hardened
against all five macro-taxonomy patterns. This closely mirrors the CPython audit's "reentrancy
family is heavily swept / mined out" conclusion — the well-fuzzed core (ext/standard, json, spl,
pcre, date, hash) is closed against exactly these patterns. One anomaly (array_walk
self-replacement → infinite loop) is **documented UB and memory-safe**, not reportable.

## Build / run

- Image: `taxoshop/php-asan-ubsan:current` = PHP **8.6.0-dev (ZTS DEBUG)**, source HEAD
  `938a3110`, clang-12 `-fsanitize=address,undefined`, `--enable-debug --enable-zts`, built via
  `Dockerfile.php`. Bakes `USE_ZEND_ALLOC=0`.
- **KEY GOTCHA — `USE_ZEND_ALLOC`.** PHP's Zend MM pools hide allocations from ASan (PHP
  analogue of CPython `PYTHONMALLOC=malloc`). Two modes:
  - `USE_ZEND_ALLOC=0` → emalloc routes to system malloc → **ASan sees heap UAF/OOB**. Use for
    reentrancy families (0014/0080/0137).
  - `USE_ZEND_ALLOC=1` → Zend MM active → at request shutdown the **debug build prints
    `=== Total N memory leaks detected ===`** for unfreed emalloc. Use for the leak family
    (0091), with `-d report_memleaks=1`.
- Run: `docker run --rm -v <php_audit1>:/audit taxoshop/php-asan-ubsan:current bash -c 'cd
  /src/php-src && USE_ZEND_ALLOC=0 ASAN_OPTIONS=detect_leaks=0:abort_on_error=1 ./sapi/cli/php
  /audit/repro/X.php'`. Grep output for `AddressSanitizer:` / `runtime error` / `Segmentation`.
- **Container leak gotcha:** a repro that hangs (infinite loop) leaves the container running —
  always wrap with `timeout N` and `docker kill` leftovers.

## The four guards that close the taxonomy in PHP

The whole reentrancy family (0014/0080/0137) fails to reproduce because PHP applies one of these
before every user-code callout:

1. **COW + `GC_ADDREF`-before-callout (arrays).** The decisive guard. Array builtins bump the
   HashTable refcount to ≥2 before running user code; any reentrant mutation via a user alias
   then hits copy-on-write and **separates into a private copy**, leaving the in-flight buffer
   untouched. Verified: `zend_array_sort_ex` (Zend/zend_hash.c:3113 `GC_ADDREF(ht)`),
   `php_implode` (`GC_TRY_ADDREF(pieces)`, materializes each `__toString` result once into an
   owned slot). `php_usort` additionally `zend_array_dup`s (array.c:835).
2. **Stable hash iterators (`zend_hash_iterator_add`).** `array_walk` (array.c:~1425) registers
   an `EG(ht_iterators)` slot that the hash layer keeps valid across rehash/realloc, does
   `ZVAL_MAKE_REF` on the value so its slot can't be freed, moves forward *before* the callback,
   and reloads `target_hash`+`pos` after ("both may have changed"). Realloc-safe by construction.
3. **`WRITE_LOCKED` / operation locks (SPL).** `SplHeap`/`SplPriorityQueue` set
   `SPL_HEAP_WRITE_LOCKED` around `compare()` and `spl_heap_consistency_validations()` throws
   *"Heap cannot be changed when it is already being modified"* on reentrant insert/extract
   (spl_heap.c:591-623). `ArrayObject::uasort` throws *"Modification of ArrayObject during
   sorting is prohibited"*. `spl_heap_elem()` also re-derives `elements+i` each access.
4. **`GC_PROTECT_RECURSION` + property snapshotting (json/serialize/var_export).** Object
   encoders take an optimized by-offset path over inline property slots (json_encoder.c:147+,
   pointers can't move) or a COW-separated properties table; nested `jsonSerialize`/`__toString`
   mutations land in a separate copy (confirmed: added props do not appear in output, no UAF).

## What was tested (all CLEAN / hardened)

Reentrancy (0014/0080/0137), ASan `USE_ZEND_ALLOC=0`, triggers = evil `__toString`/comparator/
`jsonSerialize` that grows, shrinks, clears, or self-references the target mid-operation:

| Target | Trigger | Result |
|---|---|---|
| `sort($a, SORT_STRING)` | `__toString` grows `$a` (28008 elems) | clean — COW separated (repro/h_sort_string.php) |
| `json_encode($obj)` | nested `jsonSerialize` adds 128 dyn props | clean — added props separated off (h_json_props.php) |
| `implode` | — | hardened by inspection (addref + materialize-once) |
| `array_udiff`/`array_uintersect` | comparator mutates input | COW-protected (source arrays held live) |
| `SplHeap::compare` | `compare()` calls `insert()` | throws "Heap cannot be changed" (battery1 b05 sibling) |
| `SplFixedArray` foreach | `setSize(2)` mid-loop | clean, bounded (battery3 d02) |
| `SplDoublyLinkedList`/`SplObjectStorage` | reentrant push/attach | clean (battery1 b02/b04) |
| `ArrayObject::uasort` | comparator appends | throws "Modification ... prohibited" (b05) |
| `array_multisort(SORT_STRING)` | `__toString` grows other input | clean (b03 / battery2 c05) |
| `array_intersect(SORT_STRING)` | `__toString` grows input | clean (b06) |
| `usort` self-referential + shrink | comparator sets `$a=[1]` | clean (battery3 d01) |
| `uksort` clear-in-cmp | key-compare clears `$a` | clean (d03) |
| `sort` splice-shrink to 0 | `__toString` `array_splice($a,0,4)` | clean (d05) |
| `preg_replace_callback` | callback churns pcre cache | clean (d06) |

Error-path leaks (0091), `USE_ZEND_ALLOC=1 -d report_memleaks=1`, triggers = allocate-then-fail:
`hash_init(HMAC, '')`, `array_pad(...,PHP_INT_MAX,..)`, `array_reduce`+throw, `str_repeat`
overflow, `preg_replace_callback`+throw, `json_decode` depth, `http_build_query`+throwing
`__toString`, `date_parse` garbage, `iterator_to_array`+throw, `str_pad` overflow, `sprintf`+
throwing arg, `array_map`+throw. **All 12 → 0 leaks reported.**

Thinner surfaces: `vsprintf` positional, `unpack` `C0`/`N*`, `sscanf` positional, `pack H*/a`,
`gmp_import/export`, `bcpow/bcmul`, `extract EXTR_REFS`/`compact`, `iterator_apply`+append,
`mb_str_split`/`mb_convert`. All clean.

## The one anomaly — NOT a bug

`array_walk($a, fn(&$v,$k) => $a = [...])` (replacing the walked array in the callback) →
**infinite loop / hang** (repro/battery3/d04_walk_replace.php, exit 124). Mechanism: on
replacement, `zend_hash_iterator_pos_ex(ht_iter, array)` re-associates the stable iterator with
the new array at position 0, so it re-hits key 1 → replaces again → resets → spins. **Memory is
bounded** (capping replacements terminates cleanly, d04b_probe.php; no OOB/UAF/OOM). PHP docs
explicitly declare that altering the array's *structure* inside the `array_walk` callback is
undefined and unpredictable behavior — so this is documented UB and memory-safe, not reportable.

## Family D (0077, concurrency) — not tested

The image is ZTS but CLI is single-threaded and has no `pthreads`/`parallel`, so the shared-state
races (opcache SHM, TSRM globals, signal handlers, `putenv`/`setlocale`) are not exercisable
here. Same limitation as the CPython audit (needed a dedicated TSan/free-threaded build). Would
require a ZTS + ThreadSanitizer build driven by a threaded SAPI to pursue D1–D10.

## Honest conclusion

The low/medium fruit for the reentrancy and error-path families is **exhausted in PHP's fuzzed
core**, exactly as in CPython. PHP's COW+ADDREF idiom is a particularly strong structural defense
that Ruby's mutate-in-place `Array` lacked (which is why the CRuby port found F002–F005 but the
PHP port finds nothing here). Remaining avenues are higher-effort/lower-yield: (a) a ZTS+TSan
build for family 0077; (b) less-fuzzed extensions requiring live servers (soap/ldap/snmp/
pgsql/mysqli/curl), not offline-testable in this image; (c) 0003/0007-style UBSan integer/
alignment bugs in obscure binary parsers.

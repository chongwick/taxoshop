# ruby_audit1 — NOTES

Port of the top-5 CPython macro-taxos to CRuby. Hypotheses in `Hypotheses.md` (50 total,
10 per family). Validation of tier-1 candidates below.

## FINDINGS INDEX (all confirmed on master c4e06b4e30, ASan build)

| # | Method / bug | Function (file:line) | Type | Novelty | Log | Repro |
|---|---|---|---|---|---|---|
| [F001](findings/FINDING-001-unpack-block-uaf.md) | `String#unpack` block mutates receiver | `pack_unpack_internal` pack.c:1415/1416 | heap-UAF | **DUP** of OPEN #22315 (PR #18838) | logs/h14_1.asan.txt | repro/h14_1_min.rb |
| [F002](findings/FINDING-002-flatten-toary-overflow.md) | `Array#flatten` reentrant `to_ary` | `flatten` array.c:6715 | heap-buffer-overflow | **NOVEL** (no report) | logs/h137_flatten.asan.txt | repro/h137_flatten_min.rb |
| [F003](findings/FINDING-003-zip-toary-overflow.md) | `Array#zip` (no block) reentrant `to_ary` | `rb_ary_zip` array.c:4850 | heap-buffer-overflow | **NOVEL** (no report) | logs/h137_zip.asan.txt | repro/h137_zip_min.rb |

F002+F003 are one family (stale receiver length after reentrant `to_ary`); `flatten!` is a dup of
F002. Same class as already-fixed `Array#sort!` #20427 / `Array#difference`. Best filed together.
`repro/battery/` (24) and `repro/battery2/` (24) are the broad scoping runs; all other tests clean.

## Build / run

- Image: `taxoshop/cruby-asan-ubsan:current` (ruby 4.1.0dev master `c4e06b4e30`, aarch64,
  clang `-fsanitize=address,undefined`). Built via `Dockerfile.cruby`.
- **GOTCHA — benign UBSan aborts at startup.** The build's UBSan trips on benign CRuby idioms
  and `halt_on_error=1` kills every run before the repro matters:
  - `function` check: every cfunc dispatched through a generic `VALUE(*)(int,const VALUE*,VALUE)`
    pointer (vm_insnhelper.c:3713, `exc_initialize`, etc.).
  - `alignment`/misaligned loads: `siphash.c:427/462`, iseq catch-table in `vm.c`/`compile.c`,
    `st.c:2092`, `include/ruby/internal/gc.h:685`.
  - These are NOT real bugs. Since our hunt is ASan heap-UAF, run with UBSan non-fatal + quiet:
    ```
    UBSAN_OPTIONS=halt_on_error=0:print_stacktrace=0:suppressions=/audit/ubsan.supp
    ASAN_OPTIONS=detect_leaks=0:abort_on_error=1:symbolize=1:halt_on_error=1
    ```
    `ubsan.supp` = `function:*`. ASan stays fatal, so heap-UAF still aborts (exit != 0 / prints
    `ERROR: AddressSanitizer: heap-use-after-free`). Grep the output for `AddressSanitizer:`.
- Run: `docker run --rm -v <ruby_audit1>:/audit taxoshop/cruby-asan-ubsan:current bash -c
  'cd /src/ruby && <envs> ./ruby /audit/repro/X.rb'`

## Candidate log

- **CONFIRMED but DUP — H14-1 `String#unpack` block UAF** → FINDING-001. Root cause `pack.c:1415`
  reads cached `s` after `pack.c:1416` `rb_yield`→block frees buffer; no `str_mod_check`. Det. on
  `N*/L*/Q*/V*` at ~4KB. **= OPEN #22315** (PR #18838, backport 3.4/4.0). Re-find, not novel.
  Same unpack root cause also fires via `U*`(pack.c:1494), `w*`(pack.c:1767), and `a`-directive
  (use in `str_enc_new` string.c:1109) — battery t14/t15/t16.
- **CONFIRMED + APPARENTLY NOVEL — Array#flatten heap-buffer-overflow** → FINDING-002 (battery
  t18). Element `to_ary` (via `rb_check_array_type` array.c:6705) does `ary.clear`, shrinking the
  buffer; stale split count `i` drives `ary_memcpy(result,0,i,RARRAY_CONST_PTR(ary))` (array.c:6715)
  → 16000-byte read from a 256-byte region. No flatten report upstream; same class as the
  already-fixed sort! (#20427) and difference overflows, which the sweep patched but flatten missed.
- **CONFIRMED + APPARENTLY NOVEL — Array#zip heap-buffer-overflow** → FINDING-003 (battery2 u13).
  `rb_ary_zip` captures `len=RARRAY_LEN(ary)` (array.c:4807), converts args via `take_items`→arg
  `to_ary` (array.c:4811) which `clear`s the receiver (shrinks buffer), then the NO-BLOCK loop
  `for i<len: RARRAY_AREF(ary,i)` (array.c:4850) reads past the shrunk buffer. Block branches use
  live RARRAY_LEN so are safe; no-block path is vulnerable. No zip report upstream (#13875 is a
  different GC-lifetime zip segfault). Same family as FINDING-002/#20427.
- **flatten! (battery2 u14) = DUP of FINDING-002** (calls flatten internally).
- **Battery2 (24 array-reentrancy tests) otherwise all clean:** set ops -/&/|/difference/
  intersection/union + uniq with mutating hash/eql? or block (guarded/defensive-copy); transpose,
  +, concat, replace, product, combination, permutation; reject!/select!/delete_if/keep_if block
  mutation; insert/values_at/fill evil to_int; pack buffer: kw.
- **HARDENED — H80-2 `Array#sort!` comparator mutation** — clean (fixed by #20427, backported).
- **HARDENED — H137-6 `Array#[]=` self-insert + evil `to_int`** — clean. Re-derived/copied.
- **Battery (24 tests, `repro/battery/`) all-clean except t14/t15/t16 (=unpack dup) & t18 (flatten):**
  clean = io_buffer each/each_byte/for/copy (lock-guarded), ary join(sep/elem), ary pack, sprintf
  `%.*s`, str each_byte/each_char, hash each-rehash/default-clear, ary fill-block, struct aref,
  marshal _dump-mutate, str tr, ary product/each_slice, str scan-block, pack `*`-count.

## Next leads (untested)

- H14-3/H14-4/H80-9 `IO::Buffer` `get_bytes` base retained across `#resize`/`#free` (ASan-visible,
  newer surface) — HIGH priority next.
- H137-1/H137-3/H137-4 index/length `to_int` closing/clearing receiver (`String#[]=`, `IO#read`,
  `IO#seek`) — check for existing `str_mod_check`/`rb_io_check_closed` guards first.
- H80-4/H80-5 hash/set probe with reentrant `hash`/`eql?`.
- 0091 leak family needs LeakSanitizer/valgrind (image runs `detect_leaks=0`).
- 0077 needs Ractors/threads + TSan-equivalent build.

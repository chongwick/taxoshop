# ruby_audit1 — NOTES

Port of the top-5 CPython macro-taxos to CRuby. Hypotheses in `Hypotheses.md` (50 total,
10 per family). Validation of tier-1 candidates below.

## FINDINGS INDEX (all confirmed on master c4e06b4e30, ASan build)

| # | Method / bug | Function (file:line) | Type | Novelty | Log | Repro |
|---|---|---|---|---|---|---|
| [F001](findings/FINDING-001-unpack-block-uaf.md) | `String#unpack` block mutates receiver | `pack_unpack_internal` pack.c:1415/1416 | heap-UAF | **DUP** of OPEN #22315 (PR #18838) | logs/h14_1.asan.txt | repro/h14_1_min.rb |
| [F002](findings/FINDING-002-flatten-toary-overflow.md) | `Array#flatten` reentrant `to_ary` | `flatten` array.c:6715 | heap-buffer-overflow | **NOVEL** (no report) | logs/h137_flatten.asan.txt | repro/h137_flatten_min.rb |
| [F003](findings/FINDING-003-zip-toary-overflow.md) | `Array#zip` (no block) reentrant `to_ary` | `rb_ary_zip` array.c:4850 | heap-buffer-overflow | **NOVEL** (no report) | logs/h137_zip.asan.txt | repro/h137_zip_min.rb |
| [F004](findings/FINDING-004-aref-arithseq-neglen.md) | `Array#[]` Range/ArithSeq endpoint `to_int` shrinks receiver → `len=-1` | `rb_ary_aref1`/`ary_make_partial_step` array.c:1945/1303 | heap-buffer-overflow READ + negative-length Array (SEGV) | **NOVEL** (no report) | logs/h137_aref.asan.txt | repro/h137_aref_step.rb, repro/h137_aref_neglen.rb |
| [F005](findings/FINDING-005-values-at-range-overflow.md) | `Array#values_at(Range)` endpoint `to_int` shrinks receiver; stale `olen` | `append_values_at_single`/`rb_ary_cat` array.c:3970/1417 | heap-buffer-overflow READ | **NOVEL** (no report) | logs/h137_values_at.asan.txt | repro/h137_values_at_min.rb |
| [F006](findings/FINDING-006-encode-fallback-uaf.md) | `String#encode` `:fallback` proc/Hash/[] reallocs source (live receiver) mid-transcode; cached `in_pos`/`in_stop` dangle across `goto resume` | `str_transcode0`/`transcode_loop`/`transcode_restartable0` transcode.c:2877/2433/592 | heap-use-after-free READ | **NOVEL** (no report; sibling of #22315) | logs/h_encode_fallback.asan.txt | repro/h_encode_fallback_min.rb |
| [F007](findings/FINDING-007-iobuffer-getstring-encoding-uaf.md) | `IO::Buffer#get_string` captures `base` then converts the **encoding** arg (`rb_find_encoding`→`StringValue`→`to_str`), which `resize`s (realloc-moves) the buffer; stale `base` read | `io_buffer_get_string` io_buffer.c:3262(cap)/3266(reentr)/3276(use) | heap-use-after-free READ | **NOVEL** (no report) | logs/h_iobuf_getstring.asan.txt | repro/h_iobuf_getstring_uaf.rb |
| [F008](findings/FINDING-008-pack-leb128-buffer-oob.md) | `Array#pack('r'\|'R', buffer:)` caches `start=RSTRING_LEN(res)` then element `rb_to_int` shrinks/reallocs the user `buffer:` (==res); writes `numbytes` at `RSTRING_PTR(res)+stale_start` | `pack_pack` pack.c:781(cap)/784(reentr)/800(write) → `rb_integer_pack`/`bary_pack` bignum.c:3673/911 | heap OOB WRITE (use-after-poison/wild ptr) | **NOVEL** (no report) | logs/h_pack_r_buffer.asan.txt | repro/h_pack_leb128_buffer_oob.rb |

F006 (`String#encode` `:fallback`) is the same macro-taxo in a NEW file (transcode.c): the
documented `:fallback` (proc/Hash/Method/`[]`) runs mid-transcode; the source input pointer
(`in_pos`/`in_stop = sp+slen`, cached in `str_transcode0`) is not re-fetched or `str_mod_check`ed
across the callback, so a fallback that reallocs the source (for `encode`, the live receiver)
dangles it → UAF read at transcode.c:592 after `goto resume`. Sibling of #22315 (F001, unpack).
Reachability confirmed for `encode`, `encode!`, Hash `default_proc`, and `[]`-able fallback.
Requires transcoder .so on load path: run via `run2.sh`
(`./ruby --disable-gems -I. -I.ext/aarch64-linux -I.ext/common -Ilib …`) — the base image
does NOT load enc/trans transcoders without these `-I` flags (all `encode` between distinct
encodings otherwise raises ConverterNotFound).

F002+F003 are one family (stale receiver length after reentrant `to_ary`); `flatten!` is a dup of
F002. F004 (`[]` Range/ArithSeq) and F005 (`values_at` Range) are the same broad class via reentrant
Range/ArithmeticSequence *endpoint* `to_int` shrinking the receiver; F004 is the most severe
(negative-length Array = corruption primitive). Guarded siblings prove the pattern: `slice!`
(`ary_slice_bang_by_rb_ary_splice` re-reads `orig_len` + `len<0` guard), `[]=`, `fill`.
Same umbrella as already-fixed `Array#sort!` #20427 / `Array#difference`. Best filed together.

Batteries `repro/battery{,2,3,4,5,6,8}/` are the scoping runs. Confirmed HARDENED (all clean):
strings (ljust/center/insert/tr/aset/etc — `str_modify` re-fetch), Hash rehash/transform!/update
(#21331/#21333 fixed), set ops (`-`,`&`,`|`,difference,intersection,union,product — arg converted
first, live length), `transpose`,`+`,`concat`,`replace`,`join`(fast path all-string),`to_h`,
`values_at`(Range unreachable), enum min_by/max_by/sort_by/flat_map/zip, strscan/stringio (recent
"shrunk string" fix), sprintf (`rb_str_tmp_frozen_acquire`). Only flatten/zip/aref-arithseq slipped.

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

- **DONE → F007: `IO::Buffer#get_string` base retained across encoding-arg `to_str`→`#resize`
  (realloc move) — CONFIRMED heap-UAF READ.** The reentrancy vector was NOT an index/length
  `to_int` (base is fetched after that) but the *encoding* argument, converted after base capture.
  Other IO::Buffer accessors stay hardened: `get_value`/`set_value`/`get_values`/`size_of` fetch
  base AFTER conversions; `each`/`copy` lock the buffer; `&`/`|`/`^` take an IO::Buffer mask arg
  (no user-code conversion). `rb_find_encoding` is the ONLY user-code-after-base site (io_buffer.c
  grep: line 3266 only).
- **DONE → F008: `Array#pack('r'/'R', buffer:)` heap OOB WRITE — CONFIRMED.** The `'r'`(SLEB128)/
  `'R'`(ULEB128) directives cache `start=RSTRING_LEN(res)` (pack.c:781) before `rb_to_int(from)`
  (pack.c:784, element to_int). With `buffer:` the output `res` IS the user string (pack.c:358),
  so to_int can `replace`/shrink it; `cp=RSTRING_PTR(res)+start` (pack.c:799) then `rb_integer_pack`
  writes numbytes past the buffer (bary_pack bignum.c:911). Existing pack guards (MORE_ITEM re-reads
  RARRAY_LEN; pack.c:374 "format string modified") protect the SOURCE array + FORMAT, NOT the OUTPUT
  buffer across to_int. Other directives cat via rb_str_buf_cat (re-fetch res) so are safe — only
  'r'/'R' cache a raw start/cp. Repro: `[evil].pack("r", buffer: "Z"*4096)` where evil.to_int does
  `$buf.replace("q"); 123456789`. Deterministic ASan use-after-poison WRITE.
- H137-1/H137-3/H137-4 index/length `to_int` closing/clearing receiver (`String#[]=`, `IO#read`,
  `IO#seek`) — check for existing `str_mod_check`/`rb_io_check_closed` guards first.
- H80-4/H80-5 hash/set probe with reentrant `hash`/`eql?`.
- 0091 leak family needs LeakSanitizer/valgrind (image runs `detect_leaks=0`).
- 0077 needs Ractors/threads + TSan-equivalent build.

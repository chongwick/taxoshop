# FINDING-001 — heap-use-after-free in `String#unpack` with a block that mutates the receiver

- **Status:** CONFIRMED on CRuby `master` `c4e06b4e30` (ruby 4.1.0dev, aarch64-linux), ASan build
  `taxoshop/cruby-asan-ubsan:current`. **DUPLICATE — re-find of OPEN [#22315](https://bugs.ruby-lang.org/issues/22315)**
  (identical reproducer; Peter Zhu confirmed under ASan, fix in PR #18838, backport 3.4/4.0
  REQUIRED, 3.3 WONTFIX). Not novel; retained as a successful taxonomy re-find.
- **Parent taxonomy:** `workflow-0014` / `workflow-0080` / `workflow-0137` (borrowed native
  pointer used after a re-entrant user callback frees/reallocs its backing storage). Hypothesis
  **H14-1** from `ruby_audit1/Hypotheses.md`.
- **Class match:** identical mechanism to the 2026 **Oj** gem CVEs
  (CVE-2026-54898 `Oj::Parser` SAJ-callback input mutation; CVE-2026-54897 `Oj::Doc` iterator),
  but here in **Ruby core** `pack.c`.

## Root cause

`pack_unpack_internal` (pack.c) caches the source buffer pointer once, up front:

```
pack.c:1131   s = RSTRING_PTR(str);
pack.c:1132   send = s + len;
```

The integer-directive loop (`N V n v L l Q q` and friends, all reaching the
`unpack_integer:` label) then reads through `s` and yields to the user block **inside** the
loop, without re-validating `str` afterward:

```
pack.c:1410   while (len-- > 0) {
pack.c:1415       val = rb_integer_unpack(s, integer_size, 1, 0, flags);   // <-- USE (reads *s)
pack.c:1416       UNPACK_PUSH(val);                                         // -> rb_yield(val): user block
pack.c:1417       s += integer_size;
pack.c:1418   }
```

`UNPACK_PUSH` in `UNPACK_BLOCK` mode calls `rb_yield(item_val)` (pack.c:1108–1111). If the block
mutates the receiver (`str.clear`, `str.replace(...)`, or an append that forces `realloc`), the
string's heap buffer is freed/moved via `rb_str_clear`→`str_discard`→`ruby_xfree_sized`
(string.c:6678 → 2840). On the **next** loop iteration `rb_integer_unpack(s, ...)` `memcpy`s
`integer_size` bytes from the now-dangling `s` (bignum.c:1179). There is **no `str_mod_check`**
after the yield (unlike `String#gsub`'s iter path at string.c:6350). The `pack_pack` side calls
`rb_str_modify`, but `pack_unpack_internal` has no equivalent guard.

## Reproducer (no ctypes, pure Ruby)

`ruby_audit1/repro/h14_1_min.rb`:

```ruby
s = "C" * 4000
s.unpack("L*") { s.clear }
```

A large source string makes the UAF deterministic (a small freed region is often reused by the
allocator before the next read). Confirmed across directives `N* L* Q* V*` at size 4000
(all UAF); size 64 is nondeterministically clean. `unpack1` with a block does not trip it
(returns after the first element). `C*`/`c*` (single-byte direct path) did not fault in testing.

## Sanitizer output (saved: `ruby_audit1/logs/h14_1.asan.txt`)

```
==35==ERROR: AddressSanitizer: heap-use-after-free on address 0x... 
READ of size 4 ... thread T0
    #3 bary_unpack_internal   bignum.c:1179
    #4 rb_integer_unpack      bignum.c:3753
    #5 pack_unpack_internal   pack.c:1415        <-- USE
0x... is located 4 bytes inside of 4001-byte region [...]
freed by thread T0 here:
    #2 ruby_xfree_sized       gc.c:6295
    #3 str_discard            string.c:2840
    #4 rb_str_clear           string.c:6678
    ...
    #16 rb_yield              vm_eval.c
    #17 pack_unpack_internal  pack.c:1416         <-- FREE (user block via rb_yield)
```

Same 4001-byte buffer is freed by the block and then read by the next `rb_integer_unpack`.

## Trigger conditions

- `String#unpack` (not `unpack1`) with a **block**.
- A multi-byte integer directive with a repeat count `>1` (e.g. `"L*"`, `"N*"`), so the loop
  yields at least once and then fetches again.
- The block mutates the receiver's buffer: `clear`, `replace`, or a capacity-growing append.
- Large receiver (~KBs) for deterministic reproduction.

## Fix direction (for reference; we do not patch)

Re-derive `s`/`send` from `str` after each `rb_yield`, or call a `str_mod_check(str, s, len)`
equivalent after the yield and raise `RuntimeError "string modified"` — mirroring the guard used
in `rb_str_gsub`/`rb_str_scan`. Alternatively pin the buffer with `rb_str_locktmp` for the
duration of the block.

## Duplicate analysis

- **git history (checkout):** no fix in `pack.c` for unpack + block + modify/UAF. Recent unpack
  commits (`#21979` negative offset, `#21796` `^` offset, LEB128) touched this loop without a
  mutation guard. `rb_str_modify`/`mod_check` appear only in `pack_pack`, never in
  `pack_unpack_internal`.
- **Ruby tracker (web):** the closest hit, **#13075** "String#unpack with block / unpack1
  exposes uninitialized memory", is a *distinct, already-fixed* bug (uninitialized read for
  `b/B/h/H` before content fill) — different mechanism. No report found for the
  source-mutation UAF in the integer directives.
- **Related published class:** CVE-2026-54898 / CVE-2026-54897 (Oj gem) are the same
  callback-mutates-input-during-parse UAF pattern, fixed in Oj 3.17.2 — evidence the class is
  treated as a genuine security bug when reachable from pure Ruby.
- **Caveat:** web search is not exhaustive; recommend a final manual search on
  bugs.ruby-lang.org ("unpack", "use-after-free", "unpack block") before filing.

## Not reproduced (tier-1 siblings — appear hardened on master)

- **H80-2 `Array#sort!` comparator mutation** — clean (exit 0). CRuby sorts a snapshot / detects
  mutation; `replace`/`clear`/`concat` during `<=>` did not fault.
- **H137-6 `Array#[]=` self-insert / evil `to_int`** — clean (exit 0). Splice path re-derives /
  copies; `to_int` that clears the array raised/handled without UAF.

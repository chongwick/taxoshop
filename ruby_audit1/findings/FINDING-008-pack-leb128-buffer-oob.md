# FINDING-008 — `Array#pack('r'|'R', buffer:)` heap OOB write via reentrant element `to_int`

- **Status:** CONFIRMED (ASan), APPARENTLY NOVEL
- **Class:** heap out-of-bounds WRITE (ASan: use-after-poison / wild pointer, WRITE)
- **Macro-taxo:** workflow-0137 / workflow-0014 (cached native offset/pointer used after
  reentrant user code invalidates the backing storage)
- **Target:** CRuby master `c4e06b4e30` (ruby 4.1.0dev), aarch64, clang ASan/UBSan build
  (`taxoshop/cruby-asan-ubsan:current`)
- **Component:** `pack.c` (PACK direction) + `bignum.c` (`rb_integer_pack`/`bary_pack`)
- **Repro:** `repro/h_pack_leb128_buffer_oob.rb` · **Log:** `logs/h_pack_r_buffer.asan.txt`

## Summary

`Array#pack` with the SLEB128 (`'r'`) or ULEB128 (`'R'`) integer directive and a caller-supplied
`buffer:` string caches the output write offset `start = RSTRING_LEN(res)` **before** converting
the source element with `rb_to_int` (user code). Because `res` **is** the user's `buffer:` string
(`res = buffer`, pack.c:358), the element's `to_int` can shrink or reallocate that string. The
directive then computes the destination pointer `cp = RSTRING_PTR(res) + start` from the **stale**
`start` and has `rb_integer_pack` write `numbytes` there → out-of-bounds heap write past the
(now smaller / relocated) buffer.

## Root cause

`pack_pack`, `'r'`/`'R'` case (pack.c:768-813):

```c
while (len-- > 0) {
    size_t numbytes, nlz_bits;
    int sign, extra = 0;
    char *cp;
    const long start = RSTRING_LEN(res);     // 781: cache output end (OLD length)

    from = NEXTFROM;                          // 783
    from = rb_to_int(from);                   // 784: USER CODE (element to_int)
    //     => buffer.replace(short) shrinks/reallocs res; `start` is now stale
    ...
    rb_str_modify_expand(res, numbytes + extra);  // 797: room for numbytes beyond NEW len
    cp = RSTRING_PTR(res) + start;                // 799: base + STALE start  (past buffer end)
    sign = rb_integer_pack(from, cp, numbytes, 1, 1, pack_flags);  // 800: WRITE numbytes @ cp
    ...
    while (1 < numbytes) { *cp |= 0x80; cp++; numbytes--; }        // 808-812: more OOB writes
}
```

`res = buffer` when `buffer:` is supplied (pack.c:358), and the caller retains a reference to
`buffer`, so `to_int` can mutate it. `rb_str_modify_expand(res, numbytes)` only guarantees room
for `numbytes` bytes **beyond the current (shrunk) length** — it does not restore `start` bytes.
Writing `numbytes` at offset `start > RSTRING_LEN(res)` therefore lands past the allocation.

The other integer/string directives append via `rb_str_buf_cat(res, …)`, which re-fetches
`RSTRING_PTR(res)`/length each call, so they are safe. Only `'r'`/`'R'` cache a raw `start`+`cp`
around the element conversion. (The `'w'` BER directive uses `rb_str_buf_cat` and is safe.)

## Why the existing pack guards miss it

The audit previously verified pack "hardened" because the loop re-reads `RARRAY_LEN(ary)` per
`NEXTFROM` (MORE_ITEM) and has an explicit `"format string modified"` check (pack.c:374). Those
guards protect the **source array** and the **format string** across element conversion — not the
**output buffer** `res`. The `'r'`/`'R'` directives read `res`'s length/pointer around `rb_to_int`
without any re-validation, so a reentrant mutation of the `buffer:` string is unguarded.

## ASan evidence (logs/h_pack_r_buffer.asan.txt)

```
==ERROR: AddressSanitizer: use-after-poison ... WRITE of size 1
    #0 bary_pack            bignum.c:911
    #1 rb_integer_pack      bignum.c:3673
    #2 pack_pack            pack.c:800            <- write at RSTRING_PTR(res)+stale_start
    #3 vm_opt_newarray_pack_buffer  vm_insnhelper.c:6632
Address ... is a wild pointer inside of access range of size 0x1.
```

## Reproducer (`repro/h_pack_leb128_buffer_oob.rb`)

```ruby
buf = "Z" * 4096
$buf = buf
evil = Object.new
def evil.to_int
  $buf.replace("q")     # shrink res mid-pack; start(=4096) now points past the buffer
  123456789             # multi-byte SLEB128 -> rb_integer_pack writes numbytes at res+4096
end
[evil].pack("r", buffer: buf)
```

Run: `./run.sh repro/h_pack_leb128_buffer_oob.rb`. Deterministic ASan abort. Also reachable with
`"R"` (ULEB128) and non-`*` counts; any element whose `to_int` shrinks/reallocs the `buffer:`
string works. (A drastic `replace("")` may land the write outside ASan-tracked shadow and merely
SEGV; a moderate shrink of a multi-KB buffer gives the clean use-after-poison shown above.)

## Fix options

1. Recompute the write offset from the live buffer **after** `rb_to_int`: capture
   `start = RSTRING_LEN(res)` *after* the conversion (and after `rb_str_modify_expand`), or
2. Append via a length-safe path (build the LEB128 bytes into a small local buffer, then
   `rb_str_buf_cat(res, local, numbytes)` which re-fetches `res`), or
3. Re-validate that `start <= RSTRING_LEN(res)` after the conversion and raise
   `"buffer modified"` (mirroring the pack.c:374 format-string-modified guard).

## Dup-check

No matching upstream report found for `Array#pack` `'r'`/`'R'` + `buffer:` reentrancy. Distinct
from F001/#22315 (that is the **unpack** direction — a UAF *read* when a block clears the source).
This is the **pack** direction — an OOB *write* into the output buffer, via the newer LEB128
directives and the `buffer:` keyword. Same macro-taxo family (cached offset/pointer used after
reentrant `to_int`) as F004/F005 (Array `[]`/`values_at`) and F007 (IO::Buffer `get_string`).

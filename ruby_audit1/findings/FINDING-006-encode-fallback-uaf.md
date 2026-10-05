# FINDING-006 — heap-use-after-free in `String#encode` via reentrant `:fallback`

- **Status:** CONFIRMED (ASan), APPARENTLY NOVEL (no upstream report found)
- **Target:** CRuby 4.1.0dev master `c4e06b4e30` (aarch64), clang `-fsanitize=address,undefined`
- **Class:** macro-taxo workflow-0137 / 0080 / 0014 — *reentrant user code invalidates a
  borrowed native pointer / backing storage before later use*
- **File/function:** `transcode.c` — `str_transcode0` / `transcode_loop` / `transcode_restartable0`
- **Type:** heap-use-after-free **READ** (source input buffer)
- **Log:** `logs/h_encode_fallback.asan.txt`
- **Repro:** `repro/h_encode_fallback_min.rb` (also `repro/battery18/encode_variants.rb`)

## Summary

`String#encode` (and `encode!`, `Encoding::Converter`) accept a `:fallback` option — a
`proc` / `Hash` / `Method` / any object responding to `[]` — that is invoked for each
*undefined conversion* to supply a replacement. The transcoder caches a raw pointer to the
**source** string's byte buffer and its end, then calls the user fallback mid-conversion.
If the fallback mutates the source string so its buffer is reallocated/freed, the cached
input pointer dangles; the transcoder resumes and reads through it → **heap-use-after-free**.

For `String#encode`, the source is the **live receiver** (`str_encode` starts with
`newstr = str` and only dups at the very end), so a fallback that mutates the receiver
is sufficient.

## Root cause (code path)

`str_transcode0` (transcode.c:~2872) caches the source pointer and length:

```c
fromp = sp = (unsigned char *)RSTRING_PTR(str);   /* source buffer  */
slen = RSTRING_LEN(str);
...
transcode_loop(&fromp, &bp, (sp+slen), (bp+blen), dest, ...);   /* in_stop = sp+slen */
```

`transcode_loop` (transcode.c:2415-2441):

```c
resume:
    ret = rb_econv_convert(ec, in_pos, in_stop, out_pos, out_stop, 0);   /* reads *in_pos */

    if (!NIL_P(fallback) && ret == econv_undefined_conversion) {
        ...
        rep = rb_protect(transcode_loop_fallback_try, (VALUE)&args, &state);  /* line 2433: USER CODE */
        ...
        if (!UNDEF_P(rep) && !NIL_P(rep)) {
            ret = rb_econv_insert_output(ec, ...);
            goto resume;                                                    /* re-reads *in_pos */
        }
    }
```

`transcode_loop_fallback_try` → `proc_fallback`/`hash_fallback`/`method_fallback`/
`aref_fallback` (transcode.c:2338-2352) runs arbitrary Ruby. The source buffer is **never
resized by transcode** (only the destination is, via `str_transcoding_resize`), and there is
**no re-fetch and no `str_mod_check`-style guard** on `in_pos`/`in_stop` across the fallback.
When the fallback reallocates the source, `goto resume` → `rb_econv_convert` →
`transcode_restartable0` (transcode.c:592):

```c
next_byte = (unsigned char)*in_p++;   /* in_p = dangling source pointer -> UAF read */
```

## ASan evidence

```
==ERROR: AddressSanitizer: heap-use-after-free ... READ of size 1
    #0 transcode_restartable0        transcode.c:592:36   (*in_p++)
    #1 transcode_restartable         transcode.c:828
    #2 rb_transcoding_convert        transcode.c:864
    #3 trans_sweep                   transcode.c:1191
    #4 rb_trans_conv                  transcode.c:1281
    #5 rb_econv_convert0             transcode.c:1400
    #6 rb_econv_convert              transcode.c:1508
    #7 transcode_loop                transcode.c:2417   (goto resume -> rb_econv_convert)
    #8 str_transcode0                transcode.c:2877
    #9 str_transcode                 transcode.c:2907
    #10 str_encode                   transcode.c:2973
freed by thread T0 here:
    #15 proc_fallback               transcode.c:2340   (rb_proc_call -> user code reallocs source)
    #16 transcode_loop_fallback_try transcode.c:2366
    #18 transcode_loop              transcode.c:2433
```

## Minimal reproducer

```ruby
s = "あ" * 4000                                  # heap-allocated UTF-8 source
s.encode("US-ASCII",                                  # every char = undefined conversion
         fallback: proc { |c|
           s.replace("Z" * (16 * 1024 * 1024))        # realloc/free source mid-transcode
           "?"
         })
```

Requires the transcoder extensions on the load path in this in-tree build:
`./ruby --disable-gems -I. -I.ext/aarch64-linux -I.ext/common -Ilib repro/h_encode_fallback_min.rb`

## Reachability / variants (all confirmed, same UAF at transcode.c:592)

- `String#encode(enc, fallback: proc{...})`
- `String#encode!(enc, fallback: proc{...})` (in-place)
- `fallback:` a **Hash** whose `default_proc` mutates the source (documented usage shape)
- `fallback:` an arbitrary object responding to `#[]` (`aref_fallback`)
- Expected also via `Encoding::Converter.new(src, dst, fallback: ...)#convert`.

Any UTF-8 → single-byte (US-ASCII / ISO-8859-1 / Windows-1252) conversion with non-mappable
characters reaches the fallback path.

## Fix direction

Guard the source across the fallback boundary, mirroring the guards used elsewhere for the
same reentrancy class:
- re-fetch `in_pos`/`in_stop` from the (possibly reallocated) source after the fallback and
  bail with a `RuntimeError` if the source pointer/length changed (like `str_mod_check` in
  `gsub`/`scan`, or pack's `"format string modified"` check at pack.c:374); **or**
- operate on a frozen/temp copy of the source for the duration of the transcode
  (`rb_str_tmp_frozen_acquire`, as sprintf does), **or**
- forbid mutation of the source while transcoding (freeze/lock).

## Novelty / dup-check

No upstream report matches. Related but distinct:
- **#22315** (= FINDING-001): heap-UAF in `String#unpack` with a block mutating the receiver —
  same macro-taxo, different method (pack.c). Sibling, not the same bug.
- Recent 2025 transcode fixes concern **leaks** (`rb_econv_t` leaked when the fallback *raises*,
  and "too big fallback string") — an *ownership* defect, not this source-buffer UAF.
- **#15033** is a *semantic* fallback bug (wrong char on multi-step conversions), not memory.
- Nokogiri `Document#encoding=` UAF is a Nokogiri-level issue, unrelated.

Same umbrella as FINDING-001..005: reentrant user code (here the documented `:fallback`)
invalidates a cached native buffer pointer that the operation keeps using. `transcode.c`'s
fallback path is the first non-Array/String-core site found lacking the re-fetch/mod-check
guard the maintainers apply in `pack`, `gsub`/`scan`, `io_buffer`, and `set`.

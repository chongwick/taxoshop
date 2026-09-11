# FINDING-001 — Heap out-of-bounds read in the HZ incremental decoder (`hz_decode`)

**Status:** new, confirmed under the ASan/UBSan build, no matching open/closed
issue found.
**Parent pattern:** `workflow-0036` — *"Boundary-sensitive text processing
performs speculative lookahead for a multi-element candidate without first
proving that the next element lies within the user[-supplied buffer]."*
(evidence issues #101180, #127971).
**Type:** heap-buffer-overflow, READ of size 1, one byte past a 1-byte
allocation. UB in a release build; process-aborting under ASan / hardened
allocators.
**Component:** `Modules/cjkcodecs/_codecs_cn.c` — `DECODER(hz)` (the `hz` /
`hzgb`, `hz-gb-2312` text codec).
**Affected build:** CPython `main` @ `8f847875d60` (3.16.0a0), built from the
repo `Dockerfile` target `asan-ubsan` (gcc 13.3.0, `--with-address-sanitizer
--with-undefined-behavior-sanitizer --without-pymalloc`, `PYTHONMALLOC=malloc`).
The defect exists unchanged on `main`; the file's last modification was 2023.

---

## Root cause

`Modules/cjkcodecs/_codecs_cn.c`, `DECODER(hz)`:

```c
410  DECODER(hz)
411  {
412      while (inleft > 0) {
413          unsigned char c = INBYTE1;
414          Py_UCS4 decoded;
415
416          if (c == '~') {
417              unsigned char c2 = INBYTE2;      // <-- reads (*inbuf)[1] ...
418
419              REQUIRE_INBUF(2);                // <-- ... BEFORE proving 2 bytes exist
420              if (c2 == '~' && ...)
```

The macros (`Modules/cjkcodecs/cjkcodecs.h`):

```c
#define INBYTE2 ((*inbuf)[1])                    // bare dereference of 2nd input byte
#define REQUIRE_INBUF(n) do { if (inleft < (n)) return MBERR_TOOFEW; } while (0)
```

When the input buffer holds a lone `~` (`inleft == 1`), line 417 reads
`(*inbuf)[1]`, one byte past the end of the buffer, **before** the
`REQUIRE_INBUF(2)` guard on line 419 has a chance to return `MBERR_TOOFEW`.

This is the only violation of an otherwise universal invariant in the module.
Every other cjkcodecs decoder — including the sibling GB-mode branch **in the
same function** (lines 442–443) — calls `REQUIRE_INBUF(n)` *before* any
`INBYTEn` read:

```
_codecs_cn.c:442  REQUIRE_INBUF(2);
_codecs_cn.c:443  if (TRYMAP_DEC(gb2312, decoded, c, INBYTE2)) {   // read AFTER check
```

An audit of `INBYTE2/3/4` vs `REQUIRE_INBUF` across `_codecs_{cn,hk,kr,jp,tw}.c`
(see NOTES) shows line 417 is the sole case where the read precedes the check.

### Why the incremental decoder is required to observe it

A one-shot `b'~'.decode('hz')` does **not** trip ASan: the `Py_buffer` comes
from a `bytes` object whose allocation includes a trailing NUL, so `(*inbuf)[1]`
reads that in-allocation NUL. The over-read is only observable when the lone
`~` is left *pending* by the incremental decoder and then re-decoded from the
tight, exactly-sized buffer allocated at `multibytecodec.c:1201`:

```c
1200  wsize = size + self->pendingsize;
1201  wdata = PyMem_Malloc(wsize);          // size==0, pendingsize==1  =>  malloc(1)
1206  memcpy(wdata, self->pending, self->pendingsize);   // wdata = "~"
...
1214  decoder_feed_buffer(...)              // hz_decode sees inleft==1, reads wdata[1]
```

## Reproduction (deterministic)

Minimal (`audit/repro/repro_hz_min.py`):

```python
import codecs
d = codecs.getincrementaldecoder('hz')()
d.decode(b'~', False)   # lone '~' retained as pending (pendingsize == 1)
d.decode(b'', True)     # re-decoded from malloc(1); INBYTE2 reads 1 byte past end
```

Realistic, pure-stdlib streaming trigger — any chunked/streamed `hz` decode
whose chunk boundary falls right after a `~` (e.g. network/pipe reads,
`audit/repro/repro_hz_stream.py iterdecode`):

```python
import codecs
list(codecs.iterdecode([b'~'], 'hz'))   # aborts under ASan
```

Both were reproduced deterministically; full logs in
`audit/findings/hz_asan.txt` and `audit/findings/hz_asan_iterdecode.txt`.
`b'~'.decode('hz')`, `TextIOWrapper(...).read()`, and
`codecs.getreader('hz')(...).read()` do **not** trip (they decode the whole
`bytes` buffer in one call and hit the in-allocation trailing NUL).

## Full sanitizer output (minimal repro)

```
==1==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x5020000040d1 at pc 0xffff89cdf068 bp 0xfffff26188b0 sp 0xfffff26188a0
READ of size 1 at 0x5020000040d1 thread T0
    #0 0xffff89cdf064 in hz_decode Modules/cjkcodecs/_codecs_cn.c:417
    #1 0xffff89c5426c in decoder_feed_buffer Modules/cjkcodecs/multibytecodec.c:921
    #2 0xffff89c56238 in _multibytecodec_MultibyteIncrementalDecoder_decode_impl Modules/cjkcodecs/multibytecodec.c:1214
    #3 0xffff89c56238 in _multibytecodec_MultibyteIncrementalDecoder_decode Modules/cjkcodecs/clinic/multibytecodec.c.h:395
    #4 0xaaaaeb716320 in _PyObject_VectorcallTstate Include/internal/pycore_call.h:144
    #5 0xaaaaeb716320 in PyObject_Vectorcall Objects/call.c:327
    #6 0xaaaaebd61bc8 in _Py_VectorCallInstrumentation_StackRefSteal Python/ceval.c:768
    #7 0xaaaaeb491de8 in _PyEval_EvalFrameDefault Python/generated_cases.c.h:1906
    ...
0x5020000040d1 is located 0 bytes after 1-byte region [0x5020000040d0,0x5020000040d1)
allocated by thread T0 here:
    #0 0xffff8d3d76d0 in malloc ../../../../src/libsanitizer/asan/asan_malloc_linux.cpp:69
    #1 0xffff89c56090 in _multibytecodec_MultibyteIncrementalDecoder_decode_impl Modules/cjkcodecs/multibytecodec.c:1201
    #2 0xffff89c56090 in _multibytecodec_MultibyteIncrementalDecoder_decode Modules/cjkcodecs/clinic/multibytecodec.c.h:395
    ...
SUMMARY: AddressSanitizer: heap-buffer-overflow Modules/cjkcodecs/_codecs_cn.c:417 in hz_decode
=>0x502000004080: fa fa fd fa fa fa fd fa fa fa[01]fa fa fa fa fa
==1==ABORTING
```

(Verbatim complete report, incl. shadow bytes: `audit/findings/hz_asan.txt`.)

## Match to parent pattern `workflow-0036`

- **Precondition** — input ends at the current position (`inleft == 1`) while
  the `~` escape candidate requires one more byte. ✔
- **Critical operation** — candidate probing via unvalidated next-element access
  `INBYTE2 == (*inbuf)[1]`. ✔
- **Interference** — boundary validation (`REQUIRE_INBUF(2)`) is *delayed until
  after* the probe. ✔ (matches the pattern's "delayed until after the probe").
- **Failure** — one-element-past-end OOB read, detected by ASan; functional
  correctness otherwise unaffected. ✔
- Evidence #101180 is the same defect class in the sibling `_codecs_iso2022.c`
  and was fixed there; the HZ decoder was never brought into line, so this is a
  live residual instance of the documented family — not speculation.

## Duplicate check (task requirement #4)

`gh search issues --repo python/cpython --include-prs` for: `hz_decode`,
`_codecs_cn`, `HZ codec`, `cjkcodecs buffer overflow`, `INBYTE2`,
`MultibyteIncrementalDecoder overflow`, `hz incremental decoder`,
`multibytecodec heap-buffer-overflow`, `getincrementaldecoder crash`,
`hz decode out of bounds`, `cjkcodecs read past`, `decoder_feed_buffer overflow`.
Nearest hits and why they are **not** this bug:
- #101180 (closed) — same *class*, but `_codecs_iso2022.c`; the wf-0036 evidence
  issue. Fixed there only.
- #74189 / PR #1556 (bpo-30003, merged 2017) — HZ codec *functional* escape
  handling (`~\n` line continuation); unrelated to the bounds ordering.
- #68305, #56225 — GB18030 / gb2312 decoder behavior; different codecs/bugs.
No open or closed issue/PR describes the HZ incremental-decoder over-read.
(Best-effort public-tracker search; an unpublished oss-fuzz report cannot be
excluded, but nothing is public.)

## Suggested fix

Reorder so the guard precedes the read, matching every sibling decoder:

```c
if (c == '~') {
    REQUIRE_INBUF(2);
    unsigned char c2 = INBYTE2;
    ...
```

A regression test belongs in `Lib/test/test_multibytecodec.py`
(`codecs.getincrementaldecoder('hz')().decode(b'~', False)` then
`.decode(b'', True)` must not crash and must round-trip as incomplete input).

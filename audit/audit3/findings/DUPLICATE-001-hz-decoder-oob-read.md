# DUPLICATE-001 — Heap OOB read in the HZ incremental decoder (`hz_decode`)

> **Disposition: CONFIRMED but DUPLICATE — not reportable as a new finding.**
> The bug is real and reproduces on current `main`, but it was independently
> reported upstream on 2026-09-11 as **python/cpython#157325** with fix
> **PR #157333** already open. Recorded here for completeness; **not** filed.

- **Parent pattern:** `workflow-0036` — *boundary-sensitive text processing performs
  speculative lookahead for a multi-element candidate without first proving that the next
  element lies within the input buffer.* (Evidence: #101180, #127971.)
- **Component:** `Modules/cjkcodecs/_codecs_cn.c` — `DECODER(hz)` (`hz` / `hz-gb-2312`).
- **Type:** heap-buffer-overflow, READ of size 1, one byte past a 1-byte allocation.
- **Confirmed on:** CPython `main` @ `e5d4fa281c573b764b827f3defae260787024e43`
  (3.16.0a0), image `taxoshop/cpython-asan-ubsan:current` (ASan+UBSan, `--without-pymalloc`,
  `PYTHONMALLOC=malloc`).

## Root cause

```c
DECODER(hz)
{
    while (inleft > 0) {
        unsigned char c = INBYTE1;
        ...
        if (c == '~') {
            unsigned char c2 = INBYTE2;   // _codecs_cn.c:417  reads (*inbuf)[1] ...
            REQUIRE_INBUF(2);             // _codecs_cn.c:419  ... BEFORE proving 2 bytes exist
```

`INBYTE2` expands to `((*inbuf)[1])` (a bare dereference) and `REQUIRE_INBUF(n)` is
`if (inleft < n) return MBERR_TOOFEW;`. With a lone pending `~` (`inleft == 1`), line 417
reads one byte past the buffer before line 419 can return `MBERR_TOOFEW`.

The over-read is only observable via the *incremental* decoder: the pending lone `~` is
re-decoded from a tight `malloc(size + pendingsize)` = `malloc(1)` buffer at
`multibytecodec.c:1201`. A one-shot `b'~'.decode('hz')` hits the trailing NUL inside the
`bytes` allocation and does not trip ASan.

## Uniqueness (this is the only CJK instance)

Static cross-check of `INBYTEn` vs `REQUIRE_INBUF` ordering across
`_codecs_{cn,hk,kr,jp,tw,iso2022}.c`: every other decoder guards *before* reading, and the
iso2022 escape parser proves the whole sequence in-bounds (its scan loop returns
`MBERR_TOOFEW` before computing `esclen`). `hz:417` is the sole violation. Empirically
corroborated by `repro/cjk_boundary_sweep.py` (only `hz`/`b'~'` hits).

## Reproducer — `repro/repro_hz_min.py`

```python
import codecs
d = codecs.getincrementaldecoder('hz')()
d.decode(b'~', False)   # lone '~' retained as pending (pendingsize == 1)
d.decode(b'', False)    # re-decoded from malloc(1); INBYTE2 reads 1 byte past end
```

## Sanitizer output — `logs/hz_min_asan.txt` (full report retained)

```
==1==ERROR: AddressSanitizer: heap-buffer-overflow ... READ of size 1 ...
    #0 ... in hz_decode Modules/cjkcodecs/_codecs_cn.c:417
    #1 ... in decoder_feed_buffer Modules/cjkcodecs/multibytecodec.c:921
    #2 ... in _multibytecodec_MultibyteIncrementalDecoder_decode_impl multibytecodec.c:1214
0x...d1 is located 0 bytes after 1-byte region [0x...d0,0x...d1)
allocated by thread T0 here:
    #1 ... in ..._decode_impl Modules/cjkcodecs/multibytecodec.c:1201   (malloc(1))
SUMMARY: AddressSanitizer: heap-buffer-overflow Modules/cjkcodecs/_codecs_cn.c:417 in hz_decode
```

## Duplicate determination

- **python/cpython#157325** "codecs heap buffer overflow" (OPEN, filed 2026-09-11T15:03Z):
  identical repro, identical crash site `_codecs_cn.c:417`, identical ASan trace.
- **PR #157333** "gh-157325: Fix an OOB read in the `hz` incremental decoder on a trailing
  `~`" (OPEN): the upstream fix.
- Nearest older issues (not this bug): #101180 (same *class*, fixed in `_codecs_iso2022.c`);
  #74189/#56225/#56266 (HZ functional behavior / tests, unrelated to bounds ordering).

**Conclusion:** confirmed real, but a duplicate of an open upstream issue with a fix in
flight. Not reported.

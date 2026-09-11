# DUPLICATE-002 — OOB write in `mmap` subscript assignment via re-entrant `resize()`

> **Disposition: CONFIRMED but DUPLICATE — not reportable as a new finding.**
> The bug is real and reproduces on current `main`, but it was independently
> reported upstream on 2026-09-11 as **python/cpython#157335** ("mmap segfault").
> Recorded here for completeness; **not** filed. (Original analysis:
> `audit2/findings/FINDING-001-mmap-resize-reentrancy.md`.)

- **Parent pattern:** `workflow-0137` — *reentrant argument conversion invalidates a
  backing resource before later use.* (Sub-family of `workflow-0014`.)
- **Component:** `Modules/mmapmodule.c` — `mmap_ass_subscript_lock_held`.
- **Type:** out-of-bounds WRITE (SEGV) reachable from pure Python.
- **Confirmed on:** CPython `main` @ `e5d4fa281c573b764b827f3defae260787024e43`,
  image `taxoshop/cpython-asan-ubsan:current`.

## Root cause

`mmap_ass_subscript_lock_held` validates the index `i` against `self->size`, then runs a
second user-code-executing conversion (`PyNumber_AsSsize_t(value, ...)` →
`value.__index__()`, line ~1680) before writing through `self->data`. A re-entrant
`mmap.resize()` inside that conversion `mremap`s the mapping — invalidating `self->data`
and `self->size` — but the write proceeds with the stale, pre-resize offset. `CHECK_VALID`
does not help: it only tests `self->data == NULL` (closed), and resize leaves `data != NULL`.

The slice path is analogous: `start`/`slicelen` are computed against `self->size`, then
`PyObject_GetBuffer(value, ...)` runs `value.__buffer__()` which can `resize()`, and
`safe_memcpy(self->data + start, ...)` then writes out of bounds.

## Reproducer — `audit2/repro/mmap_resize_asssub.py`

```python
import mmap
mm = mmap.mmap(-1, 100000)          # ~25 pages
class Evil:
    def __index__(self):
        mm.resize(8)                # shrink to 1 page; mapping moves
        return 0
mm[90000] = Evil()                  # index checked vs OLD size, write after resize
```

## Sanitizer output — `logs/mmap_resize_asssub_asan.txt` (full report retained)

```
==1==ERROR: AddressSanitizer: SEGV on unknown address 0x...cf90 ... WRITE memory access.
    #0 ... in safe_byte_copy Modules/mmapmodule.c:406
    #1 ... in mmap_ass_subscript_lock_held Modules/mmapmodule.c:1692
    #2 ... in mmap_ass_subscript Modules/mmapmodule.c:1750
    #3 ... in _PyEval_EvalFrameDefault Python/generated_cases.c.h:12634
SUMMARY: AddressSanitizer: SEGV Modules/mmapmodule.c:406 in safe_byte_copy
```

## Duplicate determination

- **python/cpython#157335** "mmap segfault" (OPEN, filed 2026-09-11T16:59Z): identical
  repro (`mmap(-1, 100000)`, `__index__` calling `mm.resize(8)`, `mm[90000] = ...`),
  identical crash site `mmapmodule.c:406` in `safe_byte_copy` via
  `mmap_ass_subscript_lock_held:1692` / `mmap_ass_subscript:1750`, same faulting-address
  pattern as `audit2`'s captured log.
- Nearest older issues (not this bug): #103987 / PR #103990 (fixed a `__index__` that
  *closes* the mmap — guarded only by `CHECK_VALID`, which resize evades); #118213
  (structured exception handling, Windows-only SEH). Neither covers re-entrant *resize*.

**Conclusion:** confirmed real, but a duplicate of an open upstream issue. Not reported.

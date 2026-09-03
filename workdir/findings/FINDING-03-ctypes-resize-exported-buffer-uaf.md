# Finding 03 — Use-after-free: `ctypes.resize()` reallocates a buffer still exported via the buffer protocol

> **✅ DEDUP RESULT: NOT a duplicate (determined by sanitizer crash location).**
> Crash signature (this finding):
> - **free site (root):** `_ctypes_resize_impl Modules/_ctypes/callproc.c:1923` (the `PyMem_Realloc`
>   that frees the old `b_ptr`)
> - **use site:** `memcpy` → **`PyBuffer_ToContiguous Objects/memoryobject.c:1063`** →
>   `memoryview_tobytes_impl Objects/memoryobject.c:2310`, single-thread T0, `heap-use-after-free`.
>
> No corpus/`dedups.txt` entry shares this crash location. The nearby ctypes entries are distinct:
> - `gh_113576` ("Possible heap-use-after-free in ctypes") is a **multi-threaded race** (freed by T1,
>   read by T4) during byte-swapped **type creation** (`CreateSwappedType` / `PyCSimpleType_new`);
>   only the generic `memcpy` interceptor frame coincides.
> - `gh_154524` is a **ThreadSanitizer data race** at `_ctypes.c:3129 PyCData_NewGetBuffer`, not an
>   ASan UAF at `callproc.c:1923`.
> - `gh_143005` is a **heap-buffer-overflow** at `cfield.c:644 i64_set` (array assignment `__class__`
>   swap) — different class and location.
> - `gh_143375` shares the *read* frame `memoryobject.c:1063` but is a **SEGV null-deref** via
>   `BufferedWriter.seek` re-entrant close — different error class and no `_ctypes_resize` free site.

- **Component:** `Modules/_ctypes/callproc.c` (`_ctypes.resize`) + `Modules/_ctypes/_ctypes.c`
  (`PyCData_NewGetBuffer`)
- **Bug class:** heap-use-after-free (read; write is equally reachable)
- **Detection:** AddressSanitizer, CPython `f5394c257ce` (3.15.0a1), default GIL build
- **Macro taxonomy:** [Lifetime and teardown ordering](../taxos/macro_taxos/lifetime_and_teardown.md)
  (a subsystem frees a buffer while another subsystem — the buffer-protocol consumer — still holds a
  pointer into it). Not a re-entrancy bug: no Python callback is required.

## Root cause

`ctypes` `CDataObject`s expose their raw storage through the buffer protocol:

```c
/* Modules/_ctypes/_ctypes.c : PyCData_NewGetBuffer */
view->buf = self->b_ptr;            /* raw pointer into the CData storage   */
view->obj = Py_NewRef(myself);      /* keeps the CData object alive          */
view->len = self->b_size;
```

Two facts combine into a defect:

1. **ctypes keeps no buffer-export accounting.** `PyCData_NewGetBuffer` hands out `b_ptr` but there
   is **no `bf_releasebuffer` slot** registered for CData types and **no export counter** is
   incremented. (Contrast `bytearray`/`array`/`memoryview`, which track exports and refuse mutation
   while a consumer holds a view.)

2. **`_ctypes_resize` reallocates unconditionally.** It checks only `b_needsfree`, never whether the
   storage is currently exported:

   ```c
   /* Modules/_ctypes/callproc.c : _ctypes_resize_impl */
   if (obj->b_needsfree == 0) { ...error "doesn't own it"... }
   if ((size_t)size <= sizeof(obj->b_value)) { obj->b_size = size; goto done; }  /* inline: fine */
   if (!_CDataObject_HasExternalBuffer(obj)) {
       void *ptr = PyMem_Calloc(1, size);
       memmove(ptr, obj->b_ptr, obj->b_size);
       obj->b_ptr = ptr;                 /* inline -> heap: old inline stays valid */
   } else {
       void *ptr = PyMem_Realloc(obj->b_ptr, size);   /* <-- callproc.c:1923 FREES old b_ptr */
       obj->b_ptr = ptr;                 /* heap -> heap: old block freed/moved       */
   }
   ```

When the CData object already uses an **external (heap) buffer** and `resize()` grows it, the
`PyMem_Realloc` frees/moves the old block. Any `memoryview` previously obtained from the object still
caches the **old** `view->buf`. `view->obj` keeps the CData object alive, so `resize()` runs and the
memoryview looks valid — but its `buf` now dangles. The next access
(`memoryview.tobytes()` → `PyBuffer_ToContiguous`) reads the freed region → use-after-free.

(For a *small* object the storage is inline in `b_value` and `resize` copies to a fresh heap block
without freeing anything ASan-tracked, so the bug only manifests once the initial buffer is external,
i.e. larger than `sizeof(b_value)`.)

## Reproducer

`findings/repros/ctypes_resize_uaf.py`:

```python
import ctypes

buf = (ctypes.c_char * 4096)()          # large -> heap-allocated b_ptr (external buffer)
buf[:16] = b"ABCDEFGHIJKLMNOP"
mv = memoryview(buf)                     # exports view.buf = heap b_ptr (no export accounting)
ctypes.resize(buf, 1 << 20)             # PyMem_Realloc moves+frees the old 4096-byte block
_ = [bytes(500000) for _ in range(8)]    # churn the allocator into the freed region
data = mv.tobytes()                      # reads the freed old b_ptr -> use-after-free
```

No threads and no Python callback are involved — this is a pure lifetime/ownership bug reachable from
three lines of ordinary `ctypes` code.

## Sanitizer evidence

Full log: `findings/logs/ctypes_resize_uaf.asan.txt`

```
==1279==ERROR: AddressSanitizer: heap-use-after-free on address 0x521000017d00
READ of size 4096 at 0x521000017d00 thread T0
    #0 memcpy ...sanitizer_common_interceptors_memintrinsics.inc:115
    #2 PyBuffer_ToContiguous Objects/memoryobject.c:1063
    #3 memoryview_tobytes_impl Objects/memoryobject.c:2310
    ...
0x521000017d00 is located 0 bytes inside of 4096-byte region ...
freed by thread T0 here:
    #0 realloc
    #1 _ctypes_resize_impl Modules/_ctypes/callproc.c:1923
    ...
SUMMARY: AddressSanitizer: heap-use-after-free ... in memcpy
```

## Suggested fix

Give CData objects real buffer-export accounting and make `resize` respect it:

- Register a `bf_releasebuffer` and increment/decrement an export counter in
  `PyCData_NewGetBuffer` / release, **or**
- In `_ctypes_resize_impl`, refuse to reallocate when the object is currently exported (raise
  `BufferError: Existing exports of data: object cannot be re-sized`, mirroring `bytearray`).

Either change closes the window; the second is the minimal fix at the free site `callproc.c:1923`.

## Notes / limitations

- Requires the object's storage to be an external heap buffer (initial size >
  `sizeof(CDataObject.b_value)`), which is why the reproducer starts at 4096 bytes.
- The read variant is shown; a write-after-free is equally reachable (`mv[0] = ...` on a supported
  format, or any consumer that writes through the stale view).

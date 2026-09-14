# FINDING-001 — Heap use-after-free (double `PyBuffer_Release`) receiving a memoryview from a cross-interpreter queue under OOM

- **Status:** NEW, ASan-confirmed on `taxoshop/cpython-asan-ubsan:current` (CPython 3.16.0a0, HEAD `e5d4fa28`).
- **Component:** `Modules/_interpretersmodule.c` (cross-interpreter `memoryview` XIData receive), reached via `_interpqueues` / `concurrent.interpreters` queues (also `_interpchannels`).
- **Parent pattern:** `workflow-0014` — *borrowed/derived handle used after teardown invalidates its backing storage* (error-path post-release dereference; cf. evidence #144833 "an error path decrements an object to destruction and then reads through the released pointer", #139210, #143547). Also touches the exceptional-path ownership family (0089/0091) but manifests as an **over-release / UAF**, not a leak.
- **Constraint honored:** no `ctypes`.

## Summary

When a `memoryview` (or any buffer) is sent through a cross-interpreter queue and then
received, the receiving side rebuilds a `memoryview` from the cross-interpreter data via
`_memoryview_from_xid()`. If **any allocation fails while building that target memoryview**
(e.g. under memory pressure), the shared buffer's exporter object is released **twice**,
producing a heap use-after-free (a `READ` of the freed object's type inside
`PyBuffer_Release`, and a full second release/decref of the exporter).

This is distinct from the *documented* known caveat in the same file (lines 128–132, "the
original interpreter is destroyed but code in another interpreter is still using dependent
buffers"). It also survived the recent OOM-hardening pass **gh-151126** ("Fix missing
memory errors in `_interpretersmodule.c`"), which edited these exact functions but only
converted `return NULL` → `return PyErr_NoMemory()` and did not address the double release.

## Root cause

`Modules/_interpretersmodule.c`:

1. `xibufferview_from_buffer()` (~L140) copies the incoming `Py_buffer` into the
   heap-allocated `xibufferview`, **stealing** the exporter reference:
   ```c
   /* This steals the view->obj reference  */
   *copied = *view;                 // L149-150  (copied->obj == view->view.obj)
   ```
   After this call the buffer's ownership has effectively moved into the `xibufferview`,
   **regardless of what happens next**.

2. `_memoryview_from_xid()` (~L237) marks the transfer complete only *after* success:
   ```c
   PyObject *obj = xibufferview_from_buffer(cls, &view->view, INTERPID);  // steals view->obj
   if (obj == NULL) return NULL;
   PyObject *res = PyMemoryView_FromObject(obj);
   if (res == NULL) {
       Py_DECREF(obj);              // L258  -> xibufferview_dealloc releases the stolen buffer
       return NULL;                 //         => exporter object FREED here
   }
   view->used = 1;                  // L261  (only reached on success)
   return res;
   ```
   On the failure branch, `Py_DECREF(obj)` runs `xibufferview_dealloc()` (L166), which at
   L179 calls `_PyBuffer_ReleaseInInterpreterAndRawFree(interp, self->view)` → releases the
   stolen buffer → **`Py_DECREF(exporter)` frees the exporter memoryview**. But `view->used`
   is still `0`.

3. Back in `queue_get()`, because the receive failed, the queue releases the XIData:
   `_release_xid_data` (`_interpqueuesmodule.c:1203`) → `_xidata_clear` →
   `_pybuffer_shared_free()` (L265):
   ```c
   if (!view->used) {               // still 0 -> true
       PyBuffer_Release(&view->view);   // L270  view->view.obj already freed -> UAF
   }
   ```
   `PyBuffer_Release` reads `view->view.obj->ob_type` (`_Py_TYPE_impl`) on freed memory and
   would decref/again release it.

The core invariant violation: the exporter reference is stolen in step 1, but the
`used` flag that tells the XIData cleanup "the buffer has been consumed, don't release it
again" is not set until step 2 *succeeds*. The error window between the steal and
`used = 1` double-releases the buffer.

## Reproducer

`audit5/repro/FINDING-001-repro.py` (no ctypes). The allocation failure is injected with
`_testcapi.set_nomemory()` — the same facility CPython uses to regression-test OOM paths;
the fault is reachable under genuine memory pressure.

```python
import _interpreters                 # registers memoryview as cross-interp shareable
import _interpqueues as Q
import _testcapi
buf = bytearray(b"ABCD" * 8)
qid = Q.create(10, 2, 0)             # maxsize, unboundop=ERROR, fallback=XIDATA_ONLY
Q.put(qid, memoryview(buf), 2, 0)
_testcapi.set_nomemory(3, 4)         # fail the memoryview-object allocation inside get()
try:
    Q.get(qid)
except MemoryError:
    pass
_testcapi.remove_mem_hooks()
```

Scoping (fork sweep, `audit5/repro/xibuf_fork.py`): failing allocation index **N = 3 or 4**
during `get()` aborts with ASan UAF; all other indices are clean `MemoryError`. The two
adjacent indices correspond to the `ManagedBuffer`/`memoryview` object allocations inside
`PyMemoryView_FromObject` (the allocations that happen *after* `xibufferview_getbuf` has
handed out the stolen buffer).

## Sanitizer output (saved: `audit5/logs/finding-001.asan.txt`)

```
==1==ERROR: AddressSanitizer: heap-use-after-free on address 0x510000009b58 ... READ of size 8
    #0 _Py_TYPE_impl Include/object.h:234
    #1 PyBuffer_Release Objects/abstract.c:823
    #2 _pybuffer_shared_free Modules/_interpretersmodule.c:270
    #3 _xidata_clear Python/crossinterp.c:347
    ...
    #9 _release_xid_data Modules/_interpqueuesmodule.c:49
    #10 queue_get Modules/_interpqueuesmodule.c:1203
    #11 _interpqueues_get_impl Modules/_interpqueuesmodule.c:1669

freed by thread T0 here:
    ...
    #5 xibufferview_dealloc Modules/_interpretersmodule.c:179
    #7 _memoryview_from_xid Modules/_interpretersmodule.c:258

previously allocated by thread T0 here:
    #4 memory_alloc Objects/memoryobject.c:649
    #5 mbuf_add_view Objects/memoryobject.c:691
    #7 PyMemoryView_FromObject Objects/memoryobject.c:856
```
(The freed 184-byte region is the exporter `memoryview`; it is freed on the
`_memoryview_from_xid` error branch and then read again by the queue's XIData cleanup.)

## Duplicate analysis

- **Not** the documented caveat at `_interpretersmodule.c:128-132` (that is about destroying
  the *source* interpreter while another interpreter still uses the buffer; here both live in
  one interpreter and the trigger is an allocation failure during receive).
- `git log -S "view->used"` → only the original XIData commits (gh-132776); no fix for the
  steal-vs-`used` ordering.
- Recent OOM fixes in this module — **gh-151126** ("Fix missing memory errors") and
  **gh-151842** (OOM in `capture_exception`) — touched these functions but did **not** fix
  this double release.
- `gh search issues python/cpython` for `_memoryview_from_xid`, `_pybuffer_shared`,
  `xibufferview`, "cross-interpreter buffer use-after-free" → no matching issue.

## Suggested fix (for the report; we do not patch CPython here)

Mark the buffer consumed the moment ownership is stolen, so the XIData cleanup never
double-releases. E.g. set `view->used = 1` (or `memset(&view->view, 0, sizeof)` / clear
`view->view.obj`) in `_memoryview_from_xid` **immediately after** `xibufferview_from_buffer`
succeeds — before calling `PyMemoryView_FromObject` — since `xibufferview_dealloc` now owns
the buffer regardless of success/failure. Alternatively, do not steal in
`xibufferview_from_buffer` until the memoryview is successfully built.

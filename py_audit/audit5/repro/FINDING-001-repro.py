"""
Minimal reproducer: heap use-after-free (double PyBuffer_Release) when receiving a
memoryview from a cross-interpreter queue while an allocation fails.

Root cause: Modules/_interpretersmodule.c
  - xibufferview_from_buffer() STEALS view->obj into the xibufferview's copied buffer
    (see comment "This steals the view->obj reference", ~line 149).
  - _memoryview_from_xid() only sets `view->used = 1` AFTER PyMemoryView_FromObject()
    succeeds (line ~261). If PyMemoryView_FromObject() fails (e.g. OOM building the
    target memoryview), the error branch does Py_DECREF(obj) (line ~258), and
    xibufferview_dealloc() releases the (stolen) buffer -> the exporter object is freed.
  - Because `used` is still 0, queue_get()'s cleanup then calls _pybuffer_shared_free(),
    which does PyBuffer_Release(&view->view) on the SAME (already released/freed) obj
    -> use-after-free / double release.

The allocation failure is injected deterministically with _testcapi.set_nomemory(),
the same facility CPython uses to regression-test its own OOM paths; the bug is
reachable under genuine memory pressure without any test hook.

Confirmed on taxoshop/cpython-asan-ubsan:current (CPython 3.16.0a0, HEAD e5d4fa28).
No ctypes used.
"""
import _interpreters          # registers memoryview as cross-interpreter shareable
import _interpqueues as Q
import _testcapi

buf = bytearray(b"ABCD" * 8)

qid = Q.create(10, 2, 0)                 # (maxsize, unboundop=ERROR, fallback=XIDATA_ONLY)
Q.put(qid, memoryview(buf), 2, 0)        # share the buffer into the queue

# Fail exactly the allocation that builds the target memoryview inside get().
_testcapi.set_nomemory(3, 4)
try:
    Q.get(qid)                           # -> _memoryview_from_xid -> UAF
except MemoryError:
    pass
_testcapi.remove_mem_hooks()
print("no crash (unexpected)")

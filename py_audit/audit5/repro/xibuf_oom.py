# Confirm double-DECREF UAF in _memoryview_from_xid error path (Modules/_interpretersmodule.c:257-259)
# by injecting an allocation failure at the memoryview object alloc inside _interpqueues.get().
# If the bug is real, one of the sweep values aborts the process with an ASan heap-UAF.
import _interpqueues as Q
import _testcapi
import sys

qid = Q.create(0, 2, 0)          # maxsize=0 (unbounded), unboundop=ERROR, fallback=XIDATA_ONLY
buf = bytearray(b"ABCD" * 8)

def ensure_item():
    try:
        Q.put(qid, memoryview(buf), 2, 0)
    except Exception:
        pass

for start in range(0, 400):
    ensure_item()
    _testcapi.set_nomemory(start, start + 1)   # fail exactly allocation #start
    try:
        Q.get(qid)
    except MemoryError:
        pass
    except Exception:
        pass
    finally:
        _testcapi.remove_mem_hooks()
    if start % 50 == 0:
        print("swept", start, flush=True)

print("done xibuf_oom (no crash)")

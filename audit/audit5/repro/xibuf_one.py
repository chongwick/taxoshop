import sys
start = int(sys.argv[1])
import _interpqueues as Q
import _testcapi
qid = Q.create(0, 2, 0)
buf = bytearray(b"ABCD" * 8)
Q.put(qid, memoryview(buf), 2, 0)
_testcapi.set_nomemory(start, start + 1)
try:
    Q.get(qid)
except BaseException:
    pass
finally:
    try: _testcapi.remove_mem_hooks()
    except Exception: pass
print("ok", start)

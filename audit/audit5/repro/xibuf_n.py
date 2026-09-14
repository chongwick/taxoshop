import sys
N = int(sys.argv[1])
import _interpreters
import _interpqueues as Q, _testcapi
buf = bytearray(b"ABCD" * 8)
qid = Q.create(10, 2, 0)
Q.put(qid, memoryview(buf), 2, 0)
_testcapi.set_nomemory(N, N + 1)
try:
    Q.get(qid)
except BaseException as e:
    print("py-exc", type(e).__name__)
_testcapi.remove_mem_hooks()
print("survived N", N)

import _interpreters  # registers memoryview as cross-interpreter shareable
import _interpqueues as Q, _testcapi
buf = bytearray(b"ABCD" * 8)

def fresh_q():
    return Q.create(10, 2, 0)

# Baseline: does put/get of memoryview(bytearray) work at all here?
qid = fresh_q()
try:
    Q.put(qid, memoryview(buf), 2, 0)
    got = Q.get(qid)
    print("baseline OK:", type(got[0]).__name__, bytes(got[0][:4]))
except BaseException as e:
    print("baseline FAIL:", type(e).__name__, e)

# Now: put an item, then fail exactly allocation #N during get(), for a few N.
for N in (28, 29, 30, 31, 32, 33, 34, 35, 40, 50):
    qid = fresh_q()
    try:
        Q.put(qid, memoryview(buf), 2, 0)
    except BaseException as e:
        print(f"N={N} put FAIL {type(e).__name__}"); continue
    _testcapi.set_nomemory(N, N + 1)
    try:
        Q.get(qid)
        _testcapi.remove_mem_hooks()
        print(f"N={N} get OK")
    except BaseException as e:
        _testcapi.remove_mem_hooks()
        print(f"N={N} get raised {type(e).__name__}")
print("diag done")

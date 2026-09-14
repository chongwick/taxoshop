# Step 1: confirm a memoryview can be moved through a cross-interpreter queue,
# exercising _pybuffer_shared -> _memoryview_from_xid (the code under audit).
import _interpqueues as Q
import _interpreters

# discover create() signature
import inspect
for name in ("create","put","get"):
    fn = getattr(Q, name)
    print(name, getattr(fn, "__doc__", None))

# try to create a queue and round-trip a memoryview
qid = None
# create(maxsize, unboundop, fallback): unboundop ERROR=2, fallback XIDATA_ONLY=0
for fb in (0, 1):
    try:
        qid = Q.create(10, 2, fb); print("created fallback", fb); break
    except (TypeError, ValueError) as e:
        print("create err fb", fb, e)

if qid is not None:
    print("qid", qid)
    buf = bytearray(b"ABCD"*8)
    mv = memoryview(buf)
    for putargs in ((qid, mv, 2, 0), (qid, mv, 2), (qid, mv)):
        try:
            Q.put(*putargs); print("put ok", putargs); break
        except (TypeError, ValueError) as e:
            print("put sig", putargs, e)
    try:
        got = Q.get(qid)
        print("got", type(got), got)
        obj = got[0] if isinstance(got, tuple) else got
        print("obj type", type(obj))
        if isinstance(obj, memoryview):
            print("bytes:", bytes(obj[:8]))
    except Exception as e:
        print("get err", type(e).__name__, e)
print("done plumbing")

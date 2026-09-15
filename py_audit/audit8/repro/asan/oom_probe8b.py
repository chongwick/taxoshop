# 0091 S8 pickle load_build/load_reduce error-path (raising __setstate__/append/reduce),
# S7 epoll poll result-list OOM. Watch for ASan double-free/UAF (not clean exception).
import _testcapi, pickle, os, sys

# S8a: __setstate__ raises after load_build popped state
class Boom:
    def __setstate__(self, state):
        raise RuntimeError("boom in setstate")
    def __reduce__(self):
        return (Boom, (), {"x": 1, "y": [1,2,3]})
# build a real payload once, then reload many times
for p in range(0, 6):
    try:
        payload = pickle.dumps(Boom(), protocol=p)
    except Exception:
        continue
    for _ in range(100):
        try:
            pickle.loads(payload)
        except Exception:
            pass
print("  S8a setstate-raise: clean")

# S8b: append raises during load_appends (batch)
class BadList(list):
    def append(self, x):
        raise RuntimeError("no append")
    def __reduce__(self):
        return (BadList, (), None, iter([1,2,3,4,5]))
for p in range(0, 6):
    try:
        payload = pickle.dumps(BadList([1,2,3]), protocol=p)
    except Exception:
        continue
    for _ in range(100):
        try:
            pickle.loads(payload)
        except Exception:
            pass
print("  S8b append-raise: clean")

# S8c: OOM sweep on load_build
def op_loadbuild():
    class C:
        def __reduce__(self):
            return (dict, (), {"a":1,"b":2,"c":3})
    pl = pickle.dumps(C())
    pickle.loads(pl)
for k in range(80):
    _testcapi.set_nomemory(k, k+1)
    try: op_loadbuild()
    except Exception: pass
    finally: _testcapi.remove_mem_hooks()
print("  S8c load_build OOM: swept 80 clean")

# S7: epoll poll result build under OOM
if hasattr(os, "epoll") or hasattr(__import__("select"), "epoll"):
    import select, socket
    try:
        ep = select.epoll()
        pairs = [socket.socketpair() for _ in range(8)]
        for a, b in pairs:
            ep.register(a.fileno(), select.EPOLLIN)
            b.send(b"x")
        for k in range(80):
            _testcapi.set_nomemory(k, k+1)
            try: ep.poll(0, 16)
            except Exception: pass
            finally: _testcapi.remove_mem_hooks()
        ep.close()
        for a, b in pairs: a.close(); b.close()
        print("  S7 epoll.poll OOM: swept 80 clean")
    except Exception as e:
        print("  S7 epoll: skipped", type(e).__name__, e)
else:
    print("  S7 epoll: not available")

print("oom_probe8b done")

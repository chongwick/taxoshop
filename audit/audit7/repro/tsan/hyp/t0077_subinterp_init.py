# 0077 S4/S5/S9: race one-time init of process-global extension state across subinterpreters.
# Each thread creates a fresh subinterpreter and imports the target concurrently.
import threading
try:
    from concurrent import interpreters
    make = interpreters.create
    def run(interp, code): interp.exec(code)
except Exception:
    import _interpreters as _i
    class Shim:
        def __init__(self): self.id=_i.create()
        def exec(self, code): _i.run_string(self.id, code)
    def make(): return Shim()

TARGET = __import__("sys").argv[1] if len(__import__("sys").argv)>1 else "datetime"
CODE = f"import {TARGET}"
N=8
barrier=threading.Barrier(N)
def worker():
    interp = make()
    barrier.wait()
    try:
        interp.exec(CODE)
    except Exception as e:
        print("exc", type(e).__name__, e)
ts=[threading.Thread(target=worker) for _ in range(N)]
[t.start() for t in ts]; [t.join() for t in ts]
print("done", TARGET)

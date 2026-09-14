import contextvars, threading
cvs = [contextvars.ContextVar("c%d" % i) for i in range(200)]
for i, cv in enumerate(cvs): cv.set(i)
ctx = contextvars.copy_context()
it = iter(ctx)
def worker():
    while True:
        try: next(it)
        except StopIteration: break
        except Exception: break
ts = [threading.Thread(target=worker) for _ in range(6)]
for t in ts: t.start()
for t in ts: t.join()
print("ctxvars_iter done")

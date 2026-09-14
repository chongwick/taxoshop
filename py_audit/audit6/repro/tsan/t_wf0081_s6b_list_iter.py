import threading
L = list(range(100000))
it = iter(L)
def worker():
    while True:
        try: next(it)
        except StopIteration: break
        except Exception: break
ts = [threading.Thread(target=worker) for _ in range(6)]
for t in ts: t.start()
for t in ts: t.join()
print("list_iter done")

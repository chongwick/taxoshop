import threading
d = {i: i for i in range(1000)}
it = iter(d)
stop = False
def worker():
    while not stop:
        try: next(it)
        except StopIteration: break
        except Exception: break
ts = [threading.Thread(target=worker) for _ in range(6)]
for t in ts: t.start()
for t in ts: t.join()
print("dict_iter done")

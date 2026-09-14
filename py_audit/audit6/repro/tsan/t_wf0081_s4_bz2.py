import bz2, threading
c = bz2.BZ2Compressor()
out = []
def f():
    for _ in range(2000):
        try: out.append(c.compress(b"payload" * 8))
        except Exception: break
ts = [threading.Thread(target=f) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("bz2 done")

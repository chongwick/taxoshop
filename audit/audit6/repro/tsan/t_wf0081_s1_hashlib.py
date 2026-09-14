import hashlib, threading
h = hashlib.sha256()
def f():
    for _ in range(50000): h.update(b"x")
ts = [threading.Thread(target=f) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("hashlib done:", h.hexdigest()[:16])

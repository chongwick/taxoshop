import random, threading
def f():
    for _ in range(200000): random.random()
ts = [threading.Thread(target=f) for _ in range(6)]
for t in ts: t.start()
for t in ts: t.join()
print("random done")

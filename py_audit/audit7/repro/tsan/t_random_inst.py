import random, threading
R=random.Random(42)
def f():
    for _ in range(200000): R.random(); R.getrandbits(32)
ts=[threading.Thread(target=f) for _ in range(6)]
for t in ts:t.start()
for t in ts:t.join()
print("random_inst done")

import pickle, io, threading
def f():
    p=pickle.Pickler(io.BytesIO())
    for _ in range(50000):
        try: p.dump([1,2,3,{"a":1}])
        except Exception: break
# shared pickler across threads
buf=io.BytesIO(); P=pickle.Pickler(buf)
def g():
    for _ in range(50000):
        try: P.dump((1,2,3))
        except Exception: break
ts=[threading.Thread(target=g) for _ in range(4)]
for t in ts:t.start()
for t in ts:t.join()
print("pickle done")

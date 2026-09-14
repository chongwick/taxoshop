import threading, array
a = array.array('i', range(1000))
stop = False
def grower():
    for _ in range(20000):
        a.append(1)
        if len(a) > 5000: del a[1000:]
def reader():
    while not stop:
        try: _ = a[0]; _ = a.tobytes()
        except Exception: pass
r = threading.Thread(target=reader); r.start()
g = threading.Thread(target=grower); g.start()
g.join(); stop = True; r.join()
print("array done")

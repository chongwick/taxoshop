import threading
ba = bytearray(1000)
stop = False
def grower():
    for _ in range(5000):
        ba += b"x" * 64
        del ba[1000:]
def reader():
    while not stop:
        try:
            _ = ba[0]; _ = bytes(ba[:50])
        except Exception: pass
r = threading.Thread(target=reader); r.start()
g = threading.Thread(target=grower); g.start()
g.join(); stop = True; r.join()
print("bytearray done")

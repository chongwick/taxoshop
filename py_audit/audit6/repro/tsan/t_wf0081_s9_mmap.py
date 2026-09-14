import mmap, threading
m = mmap.mmap(-1, 65536)
stop = False
def writer():
    for _ in range(50000):
        m.seek(0); m.write(b"x" * 128)
def reader():
    while not stop:
        try: m.seek(0); _ = m.read(128)
        except Exception: pass
r = threading.Thread(target=reader); r.start()
w = threading.Thread(target=writer); w.start()
w.join(); stop = True; r.join()
print("mmap done")

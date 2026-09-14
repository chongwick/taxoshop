import threading, random
L = [random.random() for _ in range(20000)]
stop = False
def sorter():
    for _ in range(200):
        L.sort()
        L.reverse()
def reader():
    while not stop:
        try:
            for x in L: pass
            _ = L[len(L)//2]
        except Exception: break
r = threading.Thread(target=reader); r.start()
s = threading.Thread(target=sorter); s.start()
s.join(); stop = True; r.join()
print("list_sort done")

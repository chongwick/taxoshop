import tracemalloc, threading
tracemalloc.start(5)
stop = False
def allocator():
    junk = []
    while not stop:
        junk.append(bytearray(100))
        if len(junk) > 500: junk.clear()
def clearer():
    for _ in range(5000):
        tracemalloc.take_snapshot()
        tracemalloc.clear_traces()
a = threading.Thread(target=allocator); a.start()
c = threading.Thread(target=clearer); c.start()
c.join(); stop = True; a.join()
tracemalloc.stop()
print("tracemalloc done")

import collections, threading
d=collections.deque(range(1000))
def a():
    for _ in range(200000):
        d.append(1)
        try: d.popleft()
        except IndexError: pass
def r():
    for _ in range(200000):
        try: _=d[0]; _=len(d); _=list(d)[:3]
        except Exception: pass
ts=[threading.Thread(target=a),threading.Thread(target=r),threading.Thread(target=a),threading.Thread(target=r)]
for t in ts:t.start()
for t in ts:t.join()
print("deque done")

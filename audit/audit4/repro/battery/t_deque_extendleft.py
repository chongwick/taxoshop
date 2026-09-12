from collections import deque
d = deque(range(10), maxlen=8)
def gen():
    yield 1
    d.clear()
    for i in range(50): yield i
d.extendleft(gen())
print("deque_extendleft ok", len(d))

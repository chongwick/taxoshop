from collections import deque
d = deque(maxlen=5)
def gen():
    for i in range(3): yield i
    d.clear()  # mutate during init
    for i in range(100): yield i
d2 = deque(gen(), maxlen=5)
print("deque_init ok", list(d2))

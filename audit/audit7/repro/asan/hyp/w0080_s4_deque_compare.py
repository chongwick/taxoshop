# 0080 S4: deque_richcompare cursor across element __eq__ that clears the deque.
# Distinct-but-equal evil objects so __eq__ actually runs (no identity shortcut).
from collections import deque
d1 = None
armed = [False]
junk = []
class Evil:
    def __eq__(self, other):
        if armed[0]:
            armed[0] = False
            d1.clear()
            # churn: allocate/free many deques to reuse freed block structs
            for _ in range(200):
                junk.append(deque(range(600)))
            del junk[:]
        return True
    def __hash__(self): return 1
# distinct evil objects at front of each deque
d1 = deque([Evil()] + list(range(400)))
d2 = deque([Evil()] + list(range(400)))
armed[0] = True
try:
    print("eq:", d1 == d2)
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s4")

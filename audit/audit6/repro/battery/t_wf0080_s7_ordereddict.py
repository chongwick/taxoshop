# wf0080 Site 7: OrderedDict node handling under key __eq__ that mutates the dict
from collections import OrderedDict
class Evil:
    def __init__(self, n): self.n = n
    def __hash__(self): return 1  # force collisions -> eq chain
    def __eq__(self, other):
        try: od.clear()
        except Exception: pass
        return False
od = OrderedDict()
for i in range(8):
    od[Evil(i)] = i
# operations that walk nodes while doing eq
try:
    od.move_to_end(Evil(0))
except Exception as e:
    print("move_to_end", type(e).__name__)
try:
    print("contains", Evil(3) in od)
except Exception as e:
    print("contains", type(e).__name__)
print("ordereddict done")

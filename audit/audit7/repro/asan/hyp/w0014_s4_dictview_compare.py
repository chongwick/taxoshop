# 0014 S4: dict view comparison (all_contained_in) borrows dv_dict/ma_keys across key __eq__.
# Unique hashes within each dict (no construction collisions); d1/d2 keys share hash so the
# membership lookup fires __eq__. Arm just before the compare.
d1 = None
armed = [False]
junk = []
class Key:
    def __init__(self, n): self.n = n
    def __hash__(self): return self.n            # unique within a dict
    def __eq__(self, other):
        if armed[0]:
            armed[0] = False
            d1.clear()
            for _ in range(200):
                junk.append({i: i for i in range(50)})
            del junk[:]
        return self.n == getattr(other, "n", None)

d1 = {Key(i): i for i in range(80)}
d2 = {Key(i): i for i in range(80)}
armed[0] = True
try:
    print("keys eq:", d1.keys() == d2.keys())
except Exception as e:
    print("exc(keys)", type(e).__name__, e)

d1 = {Key(i): i for i in range(80)}
armed[0] = True
try:
    print("items eq:", d1.items() == d2.items())
except Exception as e:
    print("exc(items)", type(e).__name__, e)
print("survived s4")

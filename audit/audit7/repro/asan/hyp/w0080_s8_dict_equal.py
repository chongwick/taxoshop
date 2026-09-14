# 0080 S8: dict_equal value compare mutates a compared dict.
# Distinct-but-equal Evil values so __eq__ runs (no identity shortcut).
d1 = None
armed = [False]
junk = []
class Evil:
    def __eq__(self, other):
        if armed[0]:
            armed[0] = False
            d1.clear()
            for _ in range(200):
                junk.append({i: i for i in range(50)})
            del junk[:]
        return True
    def __hash__(self): return 7
# distinct Evil per position; same int keys so dict_equal walks a and looks up b
d1 = {i: Evil() for i in range(80)}
d2 = {i: Evil() for i in range(80)}
armed[0] = True
try:
    print("eq:", d1 == d2)
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s8")

# 0080 S5: Counter/_count_elements key __hash__ mutates the mapping mid get->setitem
from collections import Counter
c = None
armed=[False]; junk=[]
class Evil:
    def __init__(self,n): self.n=n
    def __hash__(self):
        if armed[0]:
            armed[0]=False
            c.clear()
            for _ in range(200): junk.append({i:i for i in range(50)})
            del junk[:]
        return 5
    def __eq__(self, other): return self is other
c = Counter()
c.update(range(200))
armed[0]=True
try:
    c.update([Evil(i) for i in range(50)])
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s5")

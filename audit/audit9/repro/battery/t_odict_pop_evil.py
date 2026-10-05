from collections import OrderedDict
od = OrderedDict()
class K:
    def __init__(self,v): self.v=v
    def __hash__(self): return 1
    def __eq__(self, o):
        try: od.popitem()
        except Exception: pass
        return self.v == getattr(o,'v',o)
for i in range(30):
    od[K(i)] = i
try:
    print(od.pop(K(5), None))
except Exception as e:
    print("EXC", type(e).__name__)
print("done", len(od))

from collections import OrderedDict
class K:
    def __hash__(self): return 1
    def __eq__(self, other):
        od.clear(); return True
od = OrderedDict(); od[K()]=0; od[object()]=1
od.pop(K())
print("no crash")

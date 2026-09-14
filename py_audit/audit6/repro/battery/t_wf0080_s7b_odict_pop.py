from collections import OrderedDict
class Evil:
    def __hash__(self): return 1
    def __eq__(self, other):
        try: od.clear()
        except Exception: pass
        return False
od = OrderedDict()
for i in range(8): od[Evil()] = i
try:
    od.pop(Evil())
except Exception as e:
    print("pop", type(e).__name__, e)
print("odict pop done")

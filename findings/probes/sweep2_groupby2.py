import itertools
g = None
class Evil:
    def __init__(self, v): self.v = v
    def __eq__(self, other):
        try: next(g)   # advance during the tgtkey==currkey compare
        except Exception: pass
        return self.v == getattr(other, "v", other)
    def __hash__(self): return 0
data = [Evil(1), Evil(1), Evil(1), Evil(2)]
g = itertools.groupby(data)
try:
    k, grp = next(g)
    next(g)   # triggers compare of tgtkey/currkey while __eq__ re-advances g
except Exception as e:
    print("exc", type(e).__name__)
print("OK sweep2_groupby2")

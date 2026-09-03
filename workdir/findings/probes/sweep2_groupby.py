import itertools
g = None
class Evil:
    def __init__(self, v): self.v = v
    def __eq__(self, other):
        # re-enter: advance the same groupby iterator during key comparison
        try:
            next(g)
        except Exception:
            pass
        return isinstance(other, Evil) and self.v == other.v
    def __hash__(self): return hash(self.v)
data = [Evil(1), Evil(1), Evil(2), Evil(2), Evil(3)]
g = itertools.groupby(data)
try:
    for k, grp in g:
        list(grp)
except Exception as e:
    print("exc", type(e).__name__)
print("OK sweep2_groupby")

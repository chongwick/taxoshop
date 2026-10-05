# 0014 S5: itertools.tee shared teedataobject borrowed link across sibling consumer.
import itertools, gc

# EvilSource.__next__ manipulates the tee siblings / drops node refs mid-advance.
class EvilSource:
    def __init__(self): self.n = 0; self.branches = None
    def __iter__(self): return self
    def __next__(self):
        self.n += 1
        if self.n > 200:
            raise StopIteration
        # while branch A is advancing, mess with branch B and force GC
        if self.branches is not None:
            b = self.branches[1]
            try:
                # advance B from inside A's pull (re-entrancy attempt)
                pass
            except Exception:
                pass
        gc.collect()
        return self.n

src = EvilSource()
a, b = itertools.tee(src)
src.branches = (a, b)
try:
    out = []
    for _ in range(150):
        out.append(next(a))
        if _ % 3 == 0:
            out.append(next(b))
    print("A consumed:", len(out))
except Exception as ex:
    print("A raised:", type(ex).__name__, ex)

# Drop one branch mid-stream and keep advancing the other, forcing node free
src2 = EvilSource()
a2, b2 = itertools.tee(src2)
def evilnext():
    # drop b2 while a2 advances
    nonlocal_holder['b'] = None
    gc.collect()
nonlocal_holder = {'b': b2}
try:
    for i in range(120):
        next(a2)
        if i == 60:
            nonlocal_holder['b'] = None
            gc.collect()
    print("B ok")
except Exception as ex:
    print("B raised:", type(ex).__name__, ex)
print("0014s5 done")

import itertools
it = None
class EvilStep(int):
    fired = False
    def __radd__(self, other):
        return self
c = itertools.count(0, EvilStep(1))
# force slow path: first next() computes 0 + step
try:
    x = next(iter(c))
    print("count first:", x)
except Exception as e:
    print("count", type(e).__name__, e)

# variant per issue: step whose __add__ re-enters and mutates the count object
class Num:
    def __init__(self): pass
    def __index__(self): return 1
    def __int__(self): return 1
    def __add__(self, o): return self
    def __radd__(self, o):
        return self
try:
    c2 = itertools.count(0, Num())
    for _ in range(4): next(c2)
    print("count2 ok")
except Exception as e:
    print("count2", type(e).__name__, e)
print("count done")

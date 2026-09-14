# 0014 S2: partial_call borrowed pto->fn across the wrapped call; fn drops last ref to partial
import functools
def f(*a, **k):
    g = globals()
    g.pop('p', None)   # drop the only ref to the partial during its own call
    junk = [bytes(4096) for _ in range(50)]
    return sum(len(x) for x in junk) and 1
p = functools.partial(f, 1, 2, 3, x=4)
try:
    print(p())
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s2")

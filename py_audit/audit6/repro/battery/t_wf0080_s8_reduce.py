# wf0080 Site 8: functools.reduce reused 2-tuple across call
import functools, gc
class EvilIter:
    def __init__(self): self.i = 0
    def __iter__(self): return self
    def __next__(self):
        self.i += 1
        if self.i > 5: raise StopIteration
        gc.collect()
        return self.i
def func(acc, x):
    gc.collect()
    return acc + x
try:
    print("reduce ->", functools.reduce(func, EvilIter(), 0))
except Exception as e:
    print("reduce", type(e).__name__, e)
print("reduce done")

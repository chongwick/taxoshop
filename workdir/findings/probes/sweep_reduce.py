import functools
data = list(range(6))
class Evil:
    def __init__(self,v): self.v=v
    def __add__(self,o):
        data.clear()
        return self
def f(a,b): return a+b if not isinstance(a,Evil) else a
try: functools.reduce(lambda a,b: (data.clear(), a)[1], data, Evil(0))
except Exception as e: print("exc", type(e).__name__)
print("OK sweep_reduce")

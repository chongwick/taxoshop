import itertools
it = None
class Evil:
    def __add__(self, other):
        try: next(it)
        except Exception: pass
        return self
data = [Evil(), 1, 2, 3, 4]
it = itertools.accumulate(data)
try:
    for x in it: pass
except Exception as e:
    print("exc", type(e).__name__)
print("OK sweep2_accumulate")

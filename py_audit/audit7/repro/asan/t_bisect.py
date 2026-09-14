import bisect, sys
mode=sys.argv[1]
class Evil:
    def __init__(self,v): self.v=v
    def __lt__(self,other):
        try: arr.clear(); arr.extend(range(300))
        except Exception: pass
        return self.v < getattr(other,"v",other)
    def __gt__(self,other):
        try: arr.clear(); arr.extend(range(300))
        except Exception: pass
        return self.v > getattr(other,"v",other)
arr=list(range(50))
try:
    if mode=="insort_left": bisect.insort_left(arr, Evil(25))
    elif mode=="insort_right": bisect.insort_right(arr, Evil(25))
    elif mode=="bisect_left": bisect.bisect_left(arr, Evil(25))
    elif mode=="bisect_right": bisect.bisect_right(arr, Evil(25))
    print(mode,"done", len(arr))
except Exception as e:
    print(mode, type(e).__name__, e)

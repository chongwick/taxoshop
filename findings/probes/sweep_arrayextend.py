import array
lst=[]
class Evil:
    def __index__(self):
        lst.clear(); lst.extend([1]*5000)
        return 3
lst.extend([Evil() for _ in range(4)])
try:
    a=array.array('b'); a.extend(lst); print(len(a))
except Exception as e: print("exc", type(e).__name__)
print("OK sweep_arrayextend")

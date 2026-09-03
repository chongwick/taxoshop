# bytes(list_of_ints): each int converted via __index__; evil __index__ mutates the list
lst=[]
class Evil:
    def __index__(self):
        lst.clear(); lst.extend([1]*4000)
        return 65
lst.extend([Evil() for _ in range(4)])
try: print(len(bytes(lst)))
except Exception as e: print("exc", type(e).__name__)
print("OK sweep_bytes")

# str.join over a list; element __str__ mutates the list.
lst = []
class Evil:
    def __str__(self):
        lst.clear(); lst.extend(["y"*4000]*3)
        return "e"
lst.extend([Evil(), Evil(), Evil()])
try: print(len(" ".join(map(str, lst))))
except Exception as e: print("exc", type(e).__name__)
print("OK sweep_join")

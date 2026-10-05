import array
a = array.array('i', range(20))
class E:
    def __eq__(self, o):
        try: a.pop()
        except Exception: pass
        return False
try:
    a.index(E())
except Exception as e:
    print("EXC", type(e).__name__)
print("done", len(a))

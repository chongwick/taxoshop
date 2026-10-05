# 0080 S1: array('O') richcompare — but arrays don't support 'O' typecode.
# Fall back to object-comparison via array of same numeric type is not Python.
# array has no 'O'; test array index/contains with evil __eq__ resizing instead.
import array
class Evil:
    def __init__(self, a): self.a = a
    def __eq__(self, other):
        # resize the array mid-compare
        try: self.a.frombytes(b'\x00'*1024)
        except Exception: pass
        try: del self.a[:]
        except Exception: pass
        return False
    def __hash__(self): return 1
a = array.array('b', b'abcdefghij')
e = Evil(a)
try:
    print("contains:", e in a)
except Exception as ex:
    print("contains raised:", type(ex).__name__, ex)
a2 = array.array('b', b'abcdefghij')
e2 = Evil(a2)
try:
    print("index:", a2.index(e2))
except Exception as ex:
    print("index raised:", type(ex).__name__, ex)
print("0080s1 done")

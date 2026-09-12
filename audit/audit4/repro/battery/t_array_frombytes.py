import array
a = array.array('b', [1,2,3])
class EvilBuf:
    def __buffer__(self, flags):
        a.__init__('b', [])
        return memoryview(b"XXXX")
try:
    a.frombytes(EvilBuf())
except Exception as e:
    print("exc", type(e).__name__)
print("array_frombytes ok", len(a))

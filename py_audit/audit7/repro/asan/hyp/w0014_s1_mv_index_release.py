# 0014 S1: memoryview.index uses view after reentrant release() in __eq__
mv = None
class Evil:
    def __eq__(self, other):
        mv.release()
        return False
ba = bytearray(b"abcdefghij" * 100)
mv = memoryview(ba)
try:
    print(mv.index(Evil()))
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s1")

# 0080 S1: memoryview.count/__contains__ compare-loop reentrant release()
mv = None
class Evil:
    def __eq__(self, other):
        mv.release()
        return False
ba = bytearray(b"abcdefghij" * 100)
mv = memoryview(ba)
try:
    print(mv.count(Evil()))
except Exception as e:
    print("exc(count)", type(e).__name__, e)
ba2 = bytearray(b"xyz" * 100)
mv = memoryview(ba2)
try:
    print(Evil() in mv)
except Exception as e:
    print("exc(contains)", type(e).__name__, e)
print("survived s1")

# memoryview comparison re-entering via struct (cf. #142663) with fmt mismatch
import struct
a = memoryview(bytearray(struct.pack('4b', 1,2,3,4))).cast('b')
b = memoryview(bytearray(struct.pack('4b', 1,2,3,4))).cast('b')
class Evil:
    def __eq__(self, o):
        a.release()
        return True
try:
    print(a == b)
except Exception as e: print("exc", type(e).__name__)
print("OK mv_struct")

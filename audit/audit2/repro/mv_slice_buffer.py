ba = bytearray(b'\x00' * 64)
mv = memoryview(ba)

class Evil:
    def __buffer__(self, flags):
        mv.release()      # drop the view's hold on ba's storage
        ba.clear()        # free/realloc ba's backing buffer
        return memoryview(b'\xff' * 64)   # rvalue, matches slicelen

mv[0:64] = Evil()
print("no crash")

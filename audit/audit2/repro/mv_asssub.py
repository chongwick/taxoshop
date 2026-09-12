ba = bytearray(b'\x00' * 64)
mv = memoryview(ba)

class Evil:
    def __index__(self):
        mv.release()   # drop the view's hold on the buffer
        ba.clear()     # now allowed; frees/reallocs backing storage
        return 0

mv[Evil()] = 5
print("no crash")

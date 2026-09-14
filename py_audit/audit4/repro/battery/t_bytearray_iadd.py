ba = bytearray(b"x"*100)
class Evil:
    def __buffer__(self, flags):
        ba.clear()
        return memoryview(b"Z"*50)
try:
    ba += Evil()
    print("iadd ok", len(ba))
except Exception as e:
    print("exc", type(e).__name__)

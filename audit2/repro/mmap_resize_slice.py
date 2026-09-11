import mmap
mm = mmap.mmap(-1, 100000)

class Evil:
    def __buffer__(self, flags):
        mm.resize(8)                 # shrink after slicelen/start computed
        return memoryview(b'\x00' * 10)

mm[90000:90010] = Evil()
print("no crash")

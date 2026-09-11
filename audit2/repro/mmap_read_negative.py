import mmap
mm = mmap.mmap(-1, 100000)
class Evil:
    def __index__(self):
        mm.resize(8)
        return 90000
try:
    x = mm[Evil()]          # read path: size re-read after conversion
    print("read returned", x)
except IndexError as e:
    print("read path safe -> IndexError:", e)

import mmap
mm = mmap.mmap(-1, 8)
class Evil:
    def __index__(self):
        mm.resize(1)
        return 0
try:
    mm[3] = Evil()   # bounds checked vs old size 8, resize to 1, OOB write
except Exception as e:
    print("exc", type(e).__name__, e)
print("done-no-crash")

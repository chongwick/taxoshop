import mmap
mm = mmap.mmap(-1, 100000)   # ~25 pages
class Evil:
    def __index__(self):
        mm.resize(1)   # mremap shrink -> tail pages unmapped
        return 5
mm[90000] = Evil()   # index validated vs old size, write into unmapped tail
print("no crash")

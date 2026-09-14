import io
class EvilBuf(io.RawIOBase):
    def readable(self): return True
    n=[0]
    def readinto(self, b):
        self.n[0]+=1
        if self.n[0] > 3:
            return 0
        d=b"abc\xe4\xb8\x80def"
        b[:len(d)]=d
        try: tw.reconfigure(encoding="latin-1")
        except Exception as e: pass
        return len(d)
    def seekable(self): return False
tw = io.TextIOWrapper(io.BufferedReader(EvilBuf()), encoding="utf-8")
try:
    print("read", repr(tw.read())[:50])
except Exception as e:
    print("exc", type(e).__name__)

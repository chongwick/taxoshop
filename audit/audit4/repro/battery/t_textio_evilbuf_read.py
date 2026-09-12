import io
data = [b"hello world "*1000]
class EvilBuf(io.RawIOBase):
    def readable(self): return True
    def readinto(self, b):
        d = data[0][:len(b)]
        b[:len(d)] = d
        data[0] = data[0][len(d):]
        try: tw.detach()
        except Exception: pass
        return len(d)
    def seekable(self): return False
tw = io.TextIOWrapper(io.BufferedReader(EvilBuf()), encoding="utf-8")
try:
    print("read len", len(tw.read()))
except Exception as e:
    print("exc", type(e).__name__)

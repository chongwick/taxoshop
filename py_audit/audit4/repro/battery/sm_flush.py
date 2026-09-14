import io
class R(io.RawIOBase):
    def readable(self): return True
    def writable(self): return True
    def seekable(self): return True
    def readinto(self,b):
        tw.detach(); return 0
    def seek(self,*a):
        tw.detach(); return 0
    def tell(self):
        tw.detach(); return 0
    def truncate(self,*a):
        tw.detach(); return 0
    def flush(self):
        tw.detach()
tw=io.TextIOWrapper(io.BufferedRandom(R()),encoding="utf-8")
try:
    tw.flush() if "flush" not in ("seek","truncate") else getattr(tw,"flush")(0)
except Exception as e:
    print("exc", type(e).__name__)
print("done")

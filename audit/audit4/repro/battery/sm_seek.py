import io
ARMED=False
class R(io.RawIOBase):
    def readable(self): return True
    def writable(self): return True
    def seekable(self): return True
    def readinto(self,b):
        if ARMED: tw.detach()
        return 0
    def seek(self,*a):
        if ARMED: tw.detach()
        return 0
    def tell(self):
        if ARMED: tw.detach()
        return 0
    def truncate(self,*a):
        if ARMED: tw.detach()
        return 0
tw=io.TextIOWrapper(io.BufferedRandom(R()),encoding="utf-8")
ARMED=True
try:
    getattr(tw,"seek")(0) if "seek" in ("seek","truncate") else getattr(tw,"seek")()
except Exception as e:
    print("exc", type(e).__name__)
print("done")

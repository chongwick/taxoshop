import io
class R(io.RawIOBase):
    def readable(self): return True
    def readinto(self,b):
        tw.detach(); b[:3]=b"abc"; return 3
tw=io.TextIOWrapper(io.BufferedReader(R()),encoding="utf-8")
tw.read(2); print("NO CRASH")

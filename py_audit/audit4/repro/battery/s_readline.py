import io
class R(io.RawIOBase):
    def readable(self): return True
    def readinto(self,b):
        tw.detach(); b[:3]=b"ab\n"; return 3
tw=io.TextIOWrapper(io.BufferedReader(R()),encoding="utf-8")
tw.readline(); print("NO CRASH")

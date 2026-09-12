import io
saved=[]
class R(io.RawIOBase):
    def readable(self): return True
    def readinto(self,b):
        saved.append(tw.detach())   # keep the BufferedReader alive
        b[:3]=b"abc"; return 3
tw=io.TextIOWrapper(io.BufferedReader(R()),encoding="utf-8")
try:
    tw.read()
except Exception as e:
    print("exc", type(e).__name__)
print("NO CRASH (control)")

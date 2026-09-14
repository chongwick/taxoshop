import io
class R(io.RawIOBase):
    def writable(self): return True
    def write(self,b):
        tw.detach(); return len(b)
tw=io.TextIOWrapper(io.BufferedWriter(R()),encoding="utf-8", write_through=False)
tw.write("x"*20000); tw.flush(); print("NO CRASH")

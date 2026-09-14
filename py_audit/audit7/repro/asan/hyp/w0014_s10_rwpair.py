# 0014 S10: BufferedRWPair borrowed reader/writer across a raw callout that drops the pair
import io
pair = None
class EvilRaw(io.RawIOBase):
    def __init__(self, tag): self.tag = tag; self.buf=b"x"*100
    def readable(self): return True
    def writable(self): return True
    def readinto(self, b):
        global pair
        # drop the only external ref to the pair mid-read
        pair = None
        junk = [bytearray(4096) for _ in range(50)]
        n = min(len(b), len(self.buf))
        b[:n] = self.buf[:n]
        return n
    def write(self, b):
        return len(b)
pair = io.BufferedRWPair(EvilRaw("r"), EvilRaw("w"))
try:
    print(pair.read(10))
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s10")

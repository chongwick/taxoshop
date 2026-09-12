ba = bytearray(b"hello world "*100)
class EvilBytes:
    def __buffer__(self, flags):
        ba.clear()
        return memoryview(b"XXXX")
try:
    out = b"[%b]" % EvilBytes()
    print("out len", len(out))
except Exception as e:
    print("exc", type(e).__name__)
print("bytes_mod ok")

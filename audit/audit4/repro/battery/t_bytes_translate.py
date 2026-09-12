ba = bytearray(b"hello world "*50)
class EvilTable:
    def __buffer__(self, flags):
        ba.clear()
        return memoryview(bytes(range(256)))
try:
    out = ba.translate(EvilTable())
    print("translate len", len(out))
except Exception as e:
    print("exc", type(e).__name__)
print("bytes_translate ok")

import io
b = io.BytesIO(b"0123456789"*1000)
ba = bytearray(5000)
class EvilBuf:
    def __buffer__(self, flags):
        b.truncate(0)   # shrink BytesIO internal buffer
        return memoryview(ba)
try:
    n = b.readinto(EvilBuf())
    print("readinto ret", n)
except Exception as e:
    print("exc", type(e).__name__)
print("bytesio_readinto2 ok")

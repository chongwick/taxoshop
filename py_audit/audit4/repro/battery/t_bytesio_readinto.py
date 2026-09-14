import io
b = io.BytesIO(b"0123456789"*100)
class EvilBuf:
    def __buffer__(self, flags):
        b.close()   # close/truncate source during dest buffer acquisition
        return memoryview(bytearray(1000))
try:
    n = b.readinto(EvilBuf())
    print("readinto ret", n)
except Exception as e:
    print("exc", type(e).__name__)
print("bytesio_readinto ok")

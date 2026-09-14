class EvilBuf:
    seen=False
    def __buffer__(self, flags):
        return memoryview(b"\x01\x02\x03\x04")
print(int.from_bytes(EvilBuf(), 'big'))
print("int_frombytes ok")

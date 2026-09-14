sep = bytearray(b"-")
items = [bytearray(b"aa"), bytearray(b"bb"), bytearray(b"cc")]
class EvilPiece:
    def __buffer__(self, flags):
        sep.clear()
        items.clear()
        return memoryview(b"ZZZZ")
try:
    out = sep.join([EvilPiece(), b"xx", b"yy"])
    print("join", bytes(out))
except Exception as e:
    print("exc", type(e).__name__)
print("bytearray_join ok")

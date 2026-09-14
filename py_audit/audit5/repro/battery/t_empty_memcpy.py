# zero-length transfer through possibly-null storage (workflow-0005)
import struct, array, io
# empty containers into copy primitives
b = bytearray(0)
mv = memoryview(b)
io.BytesIO(b"").readinto(bytearray(0))
io.BytesIO().read()
bytes().join([])
b"".join([])
bytearray().join([])
bytes(b"") + b""
memoryview(b"").tobytes()
memoryview(bytearray(0)).cast('B')
a = array.array('b')
a.frombytes(b"")
a.tobytes()
struct.pack_into("", bytearray(0), 0)
struct.unpack_from("", b"")
# empty slices / copies
_ = b""[0:0]
_ = bytearray(0)[0:0]
_ = ([] * 0)
_ = (bytearray(0) * 0)
_ = (b"" * 0)
_ = memoryview(b"")[0:0].tobytes()
print("done empty_memcpy")

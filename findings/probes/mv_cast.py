ba = bytearray(range(64))
m = memoryview(ba)
try:
    c = m.cast('I')       # 4-byte view
    d = c.cast('B')
    _ = c[0], d[0]
    del c, d
except Exception as e: print("exc", type(e).__name__)
# resize the bytearray while a view exists (should be blocked), then access
ba3 = bytearray(b"y"*32); m3 = memoryview(ba3)
try:
    ba3.extend(b"z"*10000)   # must fail: existing exports
except BufferError:
    pass
except Exception as e: print("exc", type(e).__name__)
_ = bytes(m3)
print("OK mv_cast")

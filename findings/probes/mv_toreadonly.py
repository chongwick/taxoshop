ba = bytearray(b"abcd"*8)
m = memoryview(ba)
r = m.toreadonly()
m.release()
try:
    _ = bytes(r); r.release()
except Exception as e: print("exc", type(e).__name__)
# nested slice + release ordering
ba2 = bytearray(b"q"*64); base = memoryview(ba2)
s1 = base[8:56]; s2 = s1[4:40]; s3 = s2[2:20]
base.release()
try: _ = bytes(s3); s3.release(); s2.release(); s1.release()
except Exception as e: print("exc", type(e).__name__)
print("OK mv_toreadonly")

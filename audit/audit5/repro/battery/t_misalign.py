# misaligned typed access probes (workflow-0007)
import struct, array
# force an unaligned base: slice a bytearray at offset 1, cast via memoryview
buf = bytearray(64)
mv = memoryview(buf)[1:]           # base+1, odd alignment
for fmt in ('H','I','L','Q','d','f'):
    try:
        c = mv.cast(fmt)
        _ = c[0]                    # typed read at unaligned addr?
        c[0] = c[0]
        _ = c.tolist()
    except (TypeError, ValueError) as e: pass
    except Exception as e: print("mv.cast", fmt, type(e).__name__, e)
# struct unpack_from at odd offset
b = bytes(range(64))
for fmt in ('<d','<Q','<I','>d','@d','@q','@l'):
    for off in (1,3,5,7):
        try: struct.unpack_from(fmt, b, off)
        except Exception as e: print("unpack_from", fmt, off, type(e).__name__, e)
# array from unaligned bytes
try:
    a = array.array('d'); a.frombytes(bytes(64)[1:57])
except Exception as e: pass
print("done misalign")

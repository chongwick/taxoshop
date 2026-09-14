# signed left-shift UB probes (workflow-0003): decoders that accumulate bits
import marshal, pickle, struct, json
# int.from_bytes with high bit set (signed accumulation in some paths)
for n in range(1, 40):
    int.from_bytes(b"\xff"*n, 'big', signed=True)
    int.from_bytes(b"\xff"*n, 'little', signed=True)
    int.from_bytes(b"\x80"+b"\x00"*n, 'big', signed=True)
# struct signed formats near limits
for f in ('b','h','i','l','q'):
    try: struct.unpack(f, struct.pack(f, -(2**(8*struct.calcsize(f)-1))))
    except Exception: pass
# marshal round trips of extreme ints
for v in (-(2**200), 2**200-1, -1, (1<<63), -(1<<63)):
    marshal.loads(marshal.dumps(v))
# json big ints
json.loads("[" + ",".join([str(-(2**300)), str(2**300)]) + "]")
print("done shift_decode")

import struct
probes = [
  "9999999999q", "99999999999999999999q", "4611686018427387904q",
  "2305843009213693952h", "1152921504606846976i", "0q", "1000000000000d",
]
for fmt in probes:
    for fn in ("calcsize",):
        try:
            r = getattr(struct, fn)(fmt)
            print("calcsize(%r) = %r" % (fmt, r))
        except Exception as e:
            print("calcsize(%r) -> %s: %s" % (fmt, type(e).__name__, e))
# pack_into with huge offset
try:
    buf = bytearray(16)
    struct.pack_into("q", buf, 2**62, 1)
except Exception as e:
    print("pack_into huge offset ->", type(e).__name__, e)

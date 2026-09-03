import struct
tries = [
  lambda: struct.pack('>q', (1<<63)-1),
  lambda: struct.pack('>Q', (1<<64)-1),
  lambda: struct.calcsize('1000000000000q'),
  lambda: struct.pack('>i'*100, *([2**31-1]*100)),
  lambda: struct.unpack('>q', struct.pack('>q', -(1<<63))),
  lambda: struct.iter_unpack('>q', b'\x00'*80),
]
for f in tries:
    try:
        r = f()
        if hasattr(r, '__iter__') and not isinstance(r,(bytes,tuple)): list(r)
    except Exception: pass
print("OK ub_struct")

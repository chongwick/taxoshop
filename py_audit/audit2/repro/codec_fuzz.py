import encodings, pkgutil, importlib, sys
# collect codec names
names = set()
for m in pkgutil.iter_modules(encodings.__path__):
    names.add(m.name)
codecs_list = sorted(names - {"aliases","__init__"})

# crafted byte payloads that stress multibyte boundary handling
payloads = []
for base in [b"\x81", b"\x8e", b"\x8f", b"\xa1", b"\xc0", b"\xe0", b"\xf0", b"\xfe", b"\xff", b"~{", b"\x1b$"]:
    payloads.append(base)                 # 1 byte, truncated multibyte lead
    payloads.append(base + b"\x41")
    payloads.append(base + base)
    payloads.append(base*3)
    payloads.append(b"A"*10 + base)        # lead byte at very end of buffer
payloads += [b"", b"\x00", bytes(range(256))]

import codecs as _c
count=0
for name in codecs_list:
    try:
        _c.lookup(name)
    except Exception:
        continue
    for p in payloads:
        for errs in ("strict","replace","ignore"):
            try:
                p.decode(name, errs)
            except Exception:
                pass
            count+=1
print("decode probes:", count, "codecs:", len(codecs_list))

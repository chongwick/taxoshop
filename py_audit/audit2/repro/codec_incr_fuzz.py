import codecs, encodings, pkgutil
names=set()
for m in pkgutil.iter_modules(encodings.__path__):
    names.add(m.name)
codecs_list = sorted(names - {"aliases","__init__"})

seqs = [
  b"~{", b"~}", b"~{~}", b"\x1b$B", b"\x1b(B", b"\x1b$(D", b"\x0e", b"\x0f",
  b"\x81\x42", b"\x8e\xa1", b"\x8f\xa1\xa1", b"\xa1", b"\xff\xff",
  b"~{\x21\x21~}", b"\x1b$B\x21", b"\x1b", b"\x1b$", b"\x1b$(",
]
# byte-at-a-time incremental feed, then final flush
count=0
for name in codecs_list:
    try:
        dec = codecs.getincrementaldecoder(name)
    except Exception:
        continue
    for s in seqs:
        for errs in ("strict","replace","ignore"):
            try:
                d = dec(errs)
                for i,b in enumerate(s):
                    d.decode(bytes([b]), final=False)
                d.decode(b"", final=True)
            except Exception:
                pass
            count+=1
print("incremental probes:", count)

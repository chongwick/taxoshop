import codecs
# handler that returns a replacement whose length is large, into utf-16/32 writers
def handler(exc):
    return ("\U0001F600" * 1000, exc.end)
codecs.register_error("evilbig", handler)
for e in ["utf-16-le","utf-16-be","utf-32-le","utf-32-be","utf-8","cp1252"]:
    for _ in range(3):
        try: (b"\xff\xfe" + b"\x00\xd8" + b"ok").decode(e, "evilbig")
        except Exception: pass
print("OK cod_mutate")

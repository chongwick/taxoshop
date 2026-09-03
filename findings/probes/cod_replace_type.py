import codecs
# handler returns odd replacement types / mutates during handling
class Evil:
    def __len__(self): return 10**9
    def __getitem__(self, i): return "x"
def handler(exc):
    # return a bytes replacement for a decode (should be str) and huge pos
    return (b"\xff\xff", exc.end)
codecs.register_error("evilrep", handler)
for e in ["utf-8","utf-16","latin-1","ascii","unicode-escape"]:
    try: b"\xff\xff\xffabc".decode(e, "evilrep")
    except Exception: pass
def handler2(exc):
    exc.object  # touch
    return ("�", exc.start)  # no progress -> infinite? guarded to advance
codecs.register_error("evilrep2", handler2)
print("OK cod_replace_type")

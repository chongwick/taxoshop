# codec error-handler reentrancy (workflow-0080): handler mutates state / returns
# extreme positions while the codec holds writer/input pointers.
import codecs

captured = {}

def make_handler(kind):
    def h(exc):
        # mutate global codec registry state during the callback
        try: codecs.lookup("utf-8")
        except Exception: pass
        if kind == "bigrepl":
            return ("�" * 5000, exc.end)      # force writer realloc
        if kind == "backpos":
            return ("", 0)                           # rewind -> re-error loop (bounded?)
        if kind == "bytesrepl":
            return (b"?" * 3000, exc.end)
        return ("?", exc.end)
    return h

for name in ("reent_big", "reent_back", "reent_bytes"):
    pass
codecs.register_error("reent_big", make_handler("bigrepl"))
codecs.register_error("reent_bytes", make_handler("bytesrepl"))

data_bad = b"\xff\xfe\x00\x80" * 50
text_bad = "\udc80￿\U0010ffff" * 50

for enc in ("utf-8","latin-1","ascii","utf-16","utf-32","shift_jis","euc-jp","gb2312","big5"):
    for errs in ("reent_big","reent_bytes"):
        try: text_bad.encode(enc, errs)
        except Exception: pass
        try: data_bad.decode(enc, "reent_big")
        except Exception: pass

# incremental with reentrant handler
for enc in ("utf-8","shift_jis","euc-jp"):
    try:
        d = codecs.getincrementaldecoder(enc)("reent_big")
        for i in range(0, len(data_bad)):
            d.decode(data_bad[i:i+1])
        d.decode(b"", True)
    except Exception: pass

print("done codec_errh")

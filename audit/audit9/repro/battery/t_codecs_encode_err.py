# custom encode error handler that mutates globals / triggers gc during encode
import codecs, gc
hits = {"n":0}
def handler(exc):
    hits["n"] += 1
    gc.collect()
    return ("?", exc.end)
codecs.register_error("evilenc", handler)
s = "".join(chr(200+ (i%50)) for i in range(2000))  # many non-ascii -> many error calls
b = s.encode("ascii", "evilenc")
print("enc ok", len(b))

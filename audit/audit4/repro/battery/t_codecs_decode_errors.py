import codecs
def handler(exc):
    return ("　"*100, exc.end)
codecs.register_error("evilh2", handler)
data = (b"abc\xff\xfedef")*100
out = data.decode("ascii", "evilh2")
print("decode len", len(out))
print("codecs_decode ok")

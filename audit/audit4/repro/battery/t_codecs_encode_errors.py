import codecs
# custom error handler that mutates during encode
calls=[0]
def handler(exc):
    calls[0]+=1
    return ("Z"*1000, exc.end)
codecs.register_error("evilh", handler)
s = "abcሴdef噸ghi"*100
out = s.encode("ascii", "evilh")
print("encode len", len(out))
print("codecs_encode ok")

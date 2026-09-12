# incremental encoder with error handler that reenters
import codecs
enc = codecs.getincrementalencoder('ascii')('backslashreplace')
out=b""
for ch in "aГbД"*100:
    out += enc.encode(ch)
print("inc enc", len(out))
print("str_encode ok")

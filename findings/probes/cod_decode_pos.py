import codecs
# error handler returns crafted new positions to probe bounds handling in
# various decoders' error-handler call sites.
positions = [10**9, -10**9, 2**31, -(2**31)-1, 0, 5]
idx = {"i":0}
def handler(exc):
    p = positions[idx["i"] % len(positions)]; idx["i"] += 1
    return ("�", p)
codecs.register_error("evilpos", handler)
encs = ["utf-8","utf-16","utf-16-le","utf-16-be","utf-32","utf-7",
        "unicode-escape","raw-unicode-escape","ascii","latin-1","cp1252",
        "shift_jis","euc-jp","gb2312","big5","iso2022_jp"]
data = [b"\xff\xfe\xfd\xfc", b"\x80\x81\x82\x83", b"abc\xff\xffdef",
        b"\xc3\x28\xa0\xa1", b"\xed\xa0\x80", b"+\xff", b"\\x"]
for e in encs:
    for d in data:
        try: d.decode(e, "evilpos")
        except Exception: pass
print("OK cod_decode_pos")

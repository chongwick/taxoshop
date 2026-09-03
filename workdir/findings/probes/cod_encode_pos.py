import codecs
positions = [10**9, -10**9, 2**31, 0, 3]
idx={"i":0}
def handler(exc):
    p = positions[idx["i"] % len(positions)]; idx["i"] += 1
    return ("�"*3, p)
codecs.register_error("evilenc", handler)
encs = ["ascii","latin-1","utf-8","utf-16","utf-32","cp1252","shift_jis",
        "euc-jp","gb2312","big5","iso2022_jp","charmap","punycode","idna"]
strs = ["abcሴ噸xyz", "\U0001F600hello￿", "test\udc80end"]
for e in encs:
    for s in strs:
        try: s.encode(e, "evilenc")
        except Exception: pass
print("OK cod_encode_pos")

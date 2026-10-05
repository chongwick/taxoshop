import codecs

# Decode a bytearray directly (not a copy). If the utf-8 decoder does not keep
# the buffer export-locked across the error-handler call, src.clear() frees the
# storage the decoder still reads from -> UAF.
src = bytearray((b"a" * 100 + b"\xff\xff") * 500)

def handler(exc):
    try:
        src.clear()
        src.extend(b"\x00" * 4)
    except BufferError:
        pass
    return ("?", exc.end)

codecs.register_error("evil_ba", handler)
try:
    out = str(src, "utf-8", "evil_ba")
    print("decoded len", len(out))
except Exception as e:
    print("codec exc:", type(e).__name__)
print("t_codec_ba done")

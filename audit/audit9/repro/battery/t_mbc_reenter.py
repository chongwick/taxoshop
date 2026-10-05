import codecs

# CJK incremental codec: custom error handler reenters encode()/decode() on the
# SAME stateful codec object, mutating self->pending / self->state mid-operation.

def make_reentrant_handler(get_obj, feed):
    def h(exc):
        try:
            get_obj().encode(feed) if hasattr(get_obj(), "encode") else None
        except Exception:
            pass
        return ("", exc.end if hasattr(exc, "end") else 0)
    return h

# ---- incremental encoder reentrancy ----
enc = codecs.getincrementalencoder("euc_jp")("evil_enc")
def hE(exc):
    try:
        enc.encode("あ")   # reenter same encoder
    except Exception:
        pass
    return ("?", exc.end)
codecs.register_error("evil_enc", hE)
try:
    out = enc.encode("A\udc80B\udc81C")   # unencodable surrogates -> error handler
    out += enc.encode("\udc82", True)
    print("enc out", len(out))
except Exception as e:
    print("enc exc", type(e).__name__)

# ---- incremental decoder reentrancy ----
dec = codecs.getincrementaldecoder("euc_jp")("evil_dec")
def hD(exc):
    try:
        dec.decode(b"\xa4\xa2")   # reenter same decoder
    except Exception:
        pass
    return ("?", exc.end)
codecs.register_error("evil_dec", hD)
try:
    out = dec.decode(b"A\xff\xffB\x8e\xff" * 100)
    out += dec.decode(b"\xa4", True)
    print("dec out", len(out))
except Exception as e:
    print("dec exc", type(e).__name__)

# ---- stateful with reset/setstate reentrancy ----
dec2 = codecs.getincrementaldecoder("shift_jis")("evil_dec2")
def hD2(exc):
    try:
        dec2.reset()
        dec2.setstate((b"\x81", 0))
    except Exception:
        pass
    return ("?", exc.end)
codecs.register_error("evil_dec2", hD2)
try:
    print("dec2", len(dec2.decode(b"\x81\x40\xfd\xfe\xff" * 50, True)))
except Exception as e:
    print("dec2 exc", type(e).__name__)

print("t_mbc_reenter done")

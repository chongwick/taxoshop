# boundary signed-int overflow probes (workflow-0003) — values chosen to overflow
# the C size computation and raise BEFORE any large allocation happens.
def t(fn, label):
    try: fn()
    except (OverflowError, ValueError, MemoryError, TypeError) as e: pass
    except Exception as e: print(label, type(e).__name__, e)
HUGE = [2**63-1, 2**63, 2**64, 2**31* (2**33)]  # >= 2**63 so alloc can't succeed
for w in HUGE:
    t(lambda: "%*d" % (w, 1), f"str %*d w={w}")
    t(lambda: "%.*f" % (w, 1.5), f"str %.*f p={w}")
    t(lambda: b"%*d" % (w, 1), f"bytes %*d w={w}")
    t(lambda: "x".rjust(w), f"rjust {w}")
    t(lambda: "x".zfill(w), f"zfill {w}")
    t(lambda: "ab" * w, f"str*{w}")
    t(lambda: b"ab" * w, f"bytes*{w}")
    t(lambda: [0] * w, f"list*{w}")
    t(lambda: bytearray(w), f"bytearray({w})")
    t(lambda: (0,) * w, f"tuple*{w}")
print("done bound_int")

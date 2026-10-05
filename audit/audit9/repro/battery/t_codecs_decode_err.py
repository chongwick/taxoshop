# custom decode error handler; input is bytes (immutable) with many bad bytes
import codecs
def handler(exc):
    return ("?", exc.end)
codecs.register_error("evildec", handler)
data = bytes([0xff, 0x41]*1000)
u = data.decode("ascii", "evildec")
print("dec ok", len(u))

import pickle, io, sys

# Craft a pickle that: builds a big list on the stack, uses persistent id, and the
# custom persistent_load re-enters self.load()/self.find_class to churn the SHARED
# Pdata stack (push many -> realloc/free the array) while an outer opcode may hold a
# borrowed entry.
class Evil:
    def __reduce__(self):
        # persistent ref via a global that triggers find_class re-entry
        return (bytes, (b"",))

class U(pickle.Unpickler):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.n = 0
    def persistent_load(self, pid):
        self.n += 1
        if self.n < 3:
            # re-enter: churn the shared stack hard
            junk = [bytearray(i) for i in range(50)]
            return junk
        return pid
    def find_class(self, mod, name):
        # churn stack allocations during a global resolve
        _ = [tuple(range(k)) for k in range(30)]
        return super().find_class(mod, name)

# Build a stream with several PERSID ops interleaved with big collections
import pickletools
frames = []
# Manual opcodes: proto, then repeated: mark, many ints, list; persid; build lists
buf = bytearray()
buf += b'\x80\x04'                 # PROTO 4
buf += b'('                        # MARK
for i in range(40):
    buf += b'K' + bytes([i & 0xff]) # BININT1 i
buf += b'l'                        # LIST (consumes back to MARK) -> realloc heavy
buf += b'P1\n'                     # PERSID '1' -> persistent_load re-enters
buf += b'2'                        # DUP
buf += b'e' if False else b'a'     # APPEND (a): append top to list below? needs list under
buf += b'.'                        # STOP
try:
    r = U(io.BytesIO(bytes(buf))).load()
    print("pickle reentrant OK:", type(r).__name__)
except Exception as e:
    print("pickle reentrant", type(e).__name__, str(e)[:60])

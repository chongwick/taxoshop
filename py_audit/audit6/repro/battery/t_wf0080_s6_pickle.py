# wf0080 Site 6: pickle load reduce/build with persistent_load draining stack
import pickle, io
# craft: use persistent id in a pickle, persistent_load re-enters
class U(pickle.Unpickler):
    def persistent_load(self, pid):
        return list  # a callable
    def find_class(self, mod, name):
        return super().find_class(mod, name)
# Build a pickle that uses PERSID + REDUCE
data = (b'\x80\x04'          # PROTO 4
        b'P1\n'              # PERSID '1' (returns list)
        b')'                 # EMPTY_TUPLE
        b'R'                 # REDUCE -> list()
        b'.')               # STOP
try:
    r = U(io.BytesIO(data)).load()
    print("pickle ->", r)
except Exception as e:
    print("pickle", type(e).__name__, e)
print("pickle done")

import pickle, io

# During load(), a __setstate__ callback mutates unpickler.memo (clear/replace)
# while the unpickler still relies on its memo array / stack.
class Evil:
    def __setstate__(self, state):
        try:
            U[0].memo.clear()
        except Exception:
            pass
        try:
            U[0].memo = {}
        except Exception:
            pass
        self.__dict__.update(state)

# Pickle an Evil with shared/memoized substructure.
sub = {"k": [1, 2, 3]}
e = Evil()
e.__dict__ = {"a": sub, "b": sub, "c": list(range(50))}
data = pickle.dumps([e, sub, e], protocol=5)

U = [pickle.Unpickler(io.BytesIO(data))]
try:
    out = U[0].load()
    print("loaded", type(out).__name__)
except Exception as ex:
    print("unpickle exc:", type(ex).__name__, ex)
print("t_unpickle_memo done")

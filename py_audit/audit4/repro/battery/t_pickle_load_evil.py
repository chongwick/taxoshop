import pickle, io
# Build a pickle that, when loaded, uses an object whose __eq__/__hash__ reenters
class EvilKey:
    def __reduce__(self):
        return (EvilKey, ())
    def __hash__(self):
        return 1
    def __eq__(self, o):
        return False
# a dict with evil keys
d = {EvilKey(): i for i in range(20)}
data = pickle.dumps(d)
out = pickle.loads(data)
print("pickle_load ok", len(out))

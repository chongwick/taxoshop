import pickle, io
# reduce that returns a callable which, when called during load, reenters
class Reenter:
    def __reduce__(self):
        return (dict, ([(1,2),(3,4)],))
data = pickle.dumps([Reenter() for _ in range(30)])
print(len(pickle.loads(data)))
print("unpickler ok")

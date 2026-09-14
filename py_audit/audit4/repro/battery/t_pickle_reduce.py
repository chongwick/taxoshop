import pickle, io
class Evil:
    def __reduce__(self):
        return (int, (5,))
buf = io.BytesIO()
p = pickle.Pickler(buf)
lst = [Evil() for _ in range(10)]
p.dump(lst)
print("pickle_reduce ok")

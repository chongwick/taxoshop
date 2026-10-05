import pickle, io
class Evil:
    def __reduce__(self):
        d.clear()   # clear dict being pickled
        return (int, ())
d = {}
for i in range(10):
    d[i] = Evil()
try:
    pickle.dumps(d)
except Exception as e:
    print("EXC", type(e).__name__)
print("done")

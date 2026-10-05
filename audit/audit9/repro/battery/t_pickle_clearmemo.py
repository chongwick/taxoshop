import pickle, io

# During dump(), a reduce callback calls pickler.clear_memo(), which DECREFs
# every memo key and memsets the table. Probe for stale memo use / freed key.
class Bomb:
    def __reduce__(self):
        P[0].clear_memo()
        return (str, ("bomb",))

# Build a graph with many shared references so the memo is heavily populated,
# then trip clear_memo mid-dump.
shared = [object() for _ in range(200)]
payload = [shared, shared, Bomb(), shared, [shared, shared]]

buf = io.BytesIO()
P = [pickle.Pickler(buf, protocol=5)]
try:
    P[0].dump(payload)
    print("dumped", buf.tell(), "bytes")
except Exception as e:
    print("pickle exc:", type(e).__name__, e)
print("t_pickle_clearmemo done")

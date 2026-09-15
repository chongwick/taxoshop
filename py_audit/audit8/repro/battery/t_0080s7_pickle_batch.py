# 0080 S7: _pickle batch_appends / batch_setitems recursive save runs __reduce__ mid-batch,
# which mutates the container being pickled.
import pickle, io

class EvilElem:
    container = None
    def __reduce__(self):
        # mutate the list being batch-pickled
        if EvilElem.container is not None:
            try: EvilElem.container.clear()
            except Exception: pass
            try: EvilElem.container.extend([0]*2000)
            except Exception: pass
        return (int, (7,))

# batch_appends over a list
lst = []
EvilElem.container = lst
lst.extend([EvilElem() for _ in range(2000)])
try:
    print("list len before:", len(lst))
    data = pickle.dumps(lst, protocol=5)
    print("A pickled list bytes:", len(data))
except Exception as ex:
    print("A raised:", type(ex).__name__, ex)

# batch_setitems over a dict
class EvilKV:
    d = None
    def __reduce__(self):
        if EvilKV.d is not None:
            try: EvilKV.d.clear()
            except Exception: pass
        return (int, (3,))
d = {}
EvilKV.d = d
for i in range(2000):
    d[i] = EvilKV()
try:
    data = pickle.dumps(d, protocol=5)
    print("B pickled dict bytes:", len(data))
except Exception as ex:
    print("B raised:", type(ex).__name__, ex)
print("0080s7 done")

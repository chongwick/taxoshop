# list.extend(iterable) where the iterator mutates the target list
tgt=[0]
def gen():
    for i in range(10000):
        if i==1: tgt.clear()
        yield i
try: tgt.extend(gen()); print(len(tgt))
except Exception as e: print("exc", type(e).__name__)
print("OK sweep_listextend")

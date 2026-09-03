import itertools
it = None
def pred(x):
    try: next(it)
    except Exception: pass
    return True
data = [1,2,3,4,5,6]
it = itertools.dropwhile(pred, data)
try:
    for x in it: pass
except Exception as e: print("exc", type(e).__name__)
print("OK sweep2_filter")

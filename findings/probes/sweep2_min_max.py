# min/max with key callback that mutates the source list
data = list(range(30))
def key(x):
    if x == 5: data.clear()
    return x
try: print(min(data, key=key))
except Exception as e: print("exc", type(e).__name__)
data2 = list(range(30))
def key2(x):
    if x == 5: data2.clear()
    return -x
try: print(max(data2, key=key2))
except Exception as e: print("exc", type(e).__name__)
print("OK sweep2_min_max")

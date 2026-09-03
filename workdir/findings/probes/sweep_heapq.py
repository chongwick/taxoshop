# heapq.nlargest/nsmallest with key that mutates the source list
import heapq
data = list(range(50))
def key(x):
    if x==10: data.clear()
    return x
try: print(heapq.nlargest(5, data, key=key))
except Exception as e: print("exc", type(e).__name__)
data2 = list(range(50))
def key2(x):
    if x==10: data2.clear()
    return x
try: print(heapq.nsmallest(5, data2, key=key2))
except Exception as e: print("exc", type(e).__name__)
print("OK sweep_heapq")

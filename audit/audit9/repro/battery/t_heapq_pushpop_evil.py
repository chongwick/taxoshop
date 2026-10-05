import _heapq
h = [1,2,3,4,5]
_heapq.heapify(h)
class E:
    def __lt__(self, o):
        h.append(999)   # grow -> realloc
        return True
    def __gt__(self, o):
        h.append(999)
        return False
try:
    _heapq.heappush(h, E())
    _heapq.heappop(h)
except Exception as e:
    print("EXC", type(e).__name__)
print("done", len(h))

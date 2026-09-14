import heapq, sys
mode = sys.argv[1]
class Evil:
    def __init__(self, v): self.v=v
    def __lt__(self, other):
        # mutate the heap list mid-operation
        if mode in ("push","heapify","replace","pushpop"):
            try: heap.clear()          # free/realloc ob_item
            except Exception: pass
            try: heap.extend(Evil(i) for i in range(200))
            except Exception: pass
        return self.v < getattr(other,"v",other)
heap=[]
try:
    if mode=="push":
        for i in range(50): heapq.heappush(heap, Evil(i%7))
    elif mode=="heapify":
        heap=[Evil(i%7) for i in range(50)]; heapq.heapify(heap)
    elif mode=="replace":
        heap=[Evil(i%7) for i in range(50)]; heapq.heapify(heap)
        heapq.heapreplace(heap, Evil(3))
    elif mode=="pushpop":
        heap=[Evil(i%7) for i in range(50)]; heapq.heapify(heap)
        heapq.heappushpop(heap, Evil(3))
    print(mode,"done", len(heap))
except Exception as e:
    print(mode, type(e).__name__, e)

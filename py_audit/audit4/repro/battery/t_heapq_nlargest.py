import heapq
data = list(range(100))
class EvilKey:
    def __init__(self,v): self.v=v
    def __lt__(self, o):
        data.clear()
        return self.v < o.v
try:
    print(heapq.nlargest(5, [EvilKey(i) for i in range(20)]))
except Exception as e:
    print("exc", type(e).__name__)
print("nlargest ok")

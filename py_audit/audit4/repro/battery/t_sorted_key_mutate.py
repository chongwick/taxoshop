lst = list(range(50))
class K:
    def __init__(self,v): self.v=v
    def __lt__(self,o):
        lst.clear()
        return self.v<o.v
try:
    r = sorted([K(i) for i in range(30)])
    print("sorted ok", len(r))
except Exception as e:
    print("exc", type(e).__name__)

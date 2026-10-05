from collections import defaultdict
d = defaultdict(list)
class K:
    def __hash__(self): return 1
    def __eq__(self, o):
        d.clear()
        return False
# populate collisions
for i in range(20):
    d[K()].append(i)
print("len", len(d))

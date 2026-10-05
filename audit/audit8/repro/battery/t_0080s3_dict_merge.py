# 0080 S3: dict.update / dict_merge from non-dict mapping: keys()/__getitem__ mutate destination.
class EvilMapping:
    def __init__(self, dest): self.dest = dest; self._keys = [f"k{i}" for i in range(500)]
    def keys(self):
        return list(self._keys)
    def __getitem__(self, key):
        # mutate the destination dict mid-merge
        self.dest.clear()
        for i in range(1000):
            self.dest[f"x{i}"] = i
        return 42

d = {}
for i in range(50): d[f"pre{i}"] = i
em = EvilMapping(d)
try:
    d.update(em)
    print("A updated, len:", len(d))
except Exception as ex:
    print("A raised:", type(ex).__name__, ex)

# keys() returns a live view that shrinks during iteration
class EvilKeysMapping:
    def __init__(self):
        self.backing = {f"k{i}": i for i in range(500)}
    def keys(self):
        return self.backing.keys()   # live view
    def __getitem__(self, key):
        # delete other keys from backing while merge iterates keys()
        for k in list(self.backing.keys()):
            if k != key: del self.backing[k]
        return self.backing.get(key, 0)
d2 = {}
try:
    d2.update(EvilKeysMapping())
    print("B updated, len:", len(d2))
except Exception as ex:
    print("B raised:", type(ex).__name__, ex)
print("0080s3 done")

# 0080 S5: str.format / %-format field __format__/__str__ mutates the args container.
# Sharp path: format_map with an evil mapping, and %-format with a shared list via *.

class EvilFormat:
    def __init__(self, box): self.box = box
    def __format__(self, spec):
        self.box.clear()   # drop borrowed refs to the other args
        return "X"
    def __str__(self):
        self.box.clear()
        return "X"
    def __repr__(self):
        self.box.clear()
        return "X"

# Path A: "{0}{1}".format(*args) where args is a list cleared by first field's __format__
box = [EvilFormat(None), "second-borrowed-arg-value"]
box[0].box = box
try:
    print("A:", "{0}{1}".format(*box))
except Exception as ex:
    print("A raised:", type(ex).__name__, ex)

# Path B: format_map with evil mapping whose __getitem__ mutates it
class EvilMap(dict):
    def __getitem__(self, key):
        v = super().get(key, "v")
        # mutate mapping during formatting
        self.clear()
        return v
try:
    print("B:", "{a}{b}".format_map(EvilMap(a="1", b="2")))
except Exception as ex:
    print("B raised:", type(ex).__name__, ex)

# Path C: "%s%s" % tuple  (tuple immutable) vs "%(k)s" % evil mapping
class EvilPctMap(dict):
    def __getitem__(self, key):
        v = "val"
        self.clear()
        return v
try:
    print("C:", "%(a)s%(b)s" % EvilPctMap(a="1", b="2"))
except Exception as ex:
    print("C raised:", type(ex).__name__, ex)
print("0080s5 done")

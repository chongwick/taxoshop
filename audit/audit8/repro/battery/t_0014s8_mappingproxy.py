# 0014 S8: mappingproxy contains/compare/get borrows wrapped mapping across element __eq__/__hash__
# that mutates the underlying class dict (freeing ma_keys).

class Evil:
    target = None
    def __hash__(self):
        # mutate the class dict during the proxy-forwarded probe
        t = Evil.target
        if t is not None:
            for k in list(t.__dict__.keys()):
                try: delattr(t, k)
                except Exception: pass
        return 12345
    def __eq__(self, other):
        t = Evil.target
        if t is not None:
            try: t.__dict__  # no-op
            except Exception: pass
        return False

def make_class():
    class C: pass
    for i in range(64):
        setattr(C, f"attr_{i}", i)
    return C

# containment probe on a class mappingproxy
C = make_class()
Evil.target = C
mp = C.__dict__   # mappingproxy
try:
    print("A contains:", Evil() in mp)
except Exception as ex:
    print("A raised:", type(ex).__name__, ex)

# richcompare of two mappingproxies where element __eq__ mutates
C2 = make_class()
class EvilVal:
    def __eq__(self, other):
        for k in list(C2.__dict__.keys()):
            try: delattr(C2, k)
            except Exception: pass
        return False
    def __hash__(self): return 1
C2.evilval = EvilVal()
other = dict(C2.__dict__)
try:
    print("B compare:", C2.__dict__ == other)
except Exception as ex:
    print("B raised:", type(ex).__name__, ex)

# get() forwarded
C3 = make_class()
Evil.target = C3
try:
    print("C get:", C3.__dict__.get(Evil(), "default"))
except Exception as ex:
    print("C raised:", type(ex).__name__, ex)
print("0014s8 done")

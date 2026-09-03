H = 0x5150

def run(name):
    box = {}
    fires = [0]
    class Colliding:
        def __init__(self, i): self.i = i
        def __hash__(self): return H
        def __eq__(self, o):
            fires[0] += 1
            it = box.get("iter")
            if it is not None:
                it.clear()
                it.update(Filler(k) for k in range(400))  # free+realloc iterated table
            return False
    class Filler:
        def __init__(self,k): self.k=k
        def __hash__(self): return 10000+self.k
    other = set(Colliding(i) for i in range(40))    # heap-backed, iterated
    box["iter"] = other
    so = set(range(3000)); so.add(Colliding(9999))  # larger -> lookup set; colliding Evil
    if name == "intersection":
        so.intersection(other)
    elif name == "difference_update":
        so.difference_update(other)
    elif name == "symmetric_difference_update":
        so.symmetric_difference_update(other)
    elif name == "isdisjoint":
        so.isdisjoint(other)
    return fires[0]

for n in ["intersection","difference_update","symmetric_difference_update","isdisjoint"]:
    try:
        print(f"{n}: no crash (eq fired {run(n)}x)", flush=True)
    except Exception as e:
        print(f"{n}: {type(e).__name__}: {e}", flush=True)
print("DONE")

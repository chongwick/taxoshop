import sys, traceback

def check(name, fn):
    try:
        fn(); print(f"{name}: no crash", flush=True)
    except Exception as e:
        print(f"{name}: {type(e).__name__}", flush=True)

# 1) heapq.heappushpop: __lt__ clears heap
def t_heapq():
    import heapq
    h = [1,2,3,4,5,6,7,8]; heapq.heapify(h)
    class E:
        def __lt__(self, o): h.clear(); return True
        def __gt__(self, o): h.clear(); return True
    heapq.heappushpop(h, E())
def t_heapreplace():
    import heapq
    h = list(range(16)); heapq.heapify(h)
    class E:
        def __lt__(self, o): h.clear(); h.extend(range(100)); return True
        def __gt__(self, o): h.clear(); h.extend(range(100)); return True
    heapq.heapreplace(h, E())

# 2) max/min with key that mutates the source list
def t_max_key():
    data = [object() for _ in range(32)]
    def key(o):
        data.clear()   # drop refs to remaining items
        return 1
    max(data, key=key)
def t_min_key():
    data = [object() for _ in range(32)]
    def key(o):
        data.clear(); return 1
    min(data, key=key)

# 3) dict.update with an evil mapping whose keys() mutates
def t_dict_update():
    d = {}
    class M:
        def keys(self):
            return EvilKeys()
        def __getitem__(self, k): return 1
    class EvilKeys:
        def __init__(self): self.n=0
        def __iter__(self): return self
        def __next__(self):
            self.n+=1
            if self.n>3: raise StopIteration
            d.clear()
            return object()
    d.update(M())

# 4) json decoder object_pairs_hook mutating
def t_json_hook():
    import json
    def oph(pairs):
        raise ValueError("x")
    try:
        json.loads(b"{\"a\": 1, \"b\": 2}", object_pairs_hook=oph)
    except ValueError: pass

# 5) sorted with key mutating (list.sort protects, but sorted over evil iter)
def t_sorted_key():
    data = [object() for _ in range(32)]
    def key(o):
        data.clear(); return 1
    sorted(data, key=key)

# 6) tuple/list repeat via __index__ (array covered; test list)
def t_list_repeat():
    lst = [1,2,3]
    class I:
        def __index__(self):
            lst.clear(); return 1000000
    lst2 = lst * I()

for n,f in [("heappushpop",t_heapq),("heapreplace",t_heapreplace),("max_key",t_max_key),
            ("min_key",t_min_key),("dict_update",t_dict_update),("json_oph",t_json_hook),
            ("sorted_key",t_sorted_key),("list_repeat",t_list_repeat)]:
    check(n,f)
print("DONE")

import sys

def build(target_mutator, n=64):
    # iterated set S has many keys (heap table); one colliding "hot" key
    # lookup set L contains Evil (same hash as hot key) -> forces __eq__
    class Evil:
        def __hash__(self): return 0x1234
        def __eq__(self, o):
            target_mutator()
            return False
    class Hot:
        def __hash__(self): return 0x1234
        def __eq__(self, o):
            target_mutator()
            return False
    return Evil, Hot

def run(name, op):
    print(f"--- {name} ---", flush=True)
    try:
        op()
        print(f"{name}: no crash", flush=True)
    except Exception as e:
        print(f"{name}: {type(e).__name__}: {e}", flush=True)

# 1) intersection: iterate `other`, lookup in `so`; Evil in so mutates other
def t_intersection():
    S = set(range(64))                      # heap table, iterated
    class Evil:
        def __hash__(self): return 7
        def __eq__(self, o):
            S.clear(); S.update(range(200))  # free+realloc the iterated table
            return False
    S.add(7)                                # key in S with hash 7 (int 7 hashes to 7)
    L = set(range(1000)); L.add(Evil())     # larger -> becomes lookup set
    return S.intersection(L)

# 2) difference_update: iterate other, discard from so
def t_diff_update():
    S = set(); 
    class Evil:
        def __hash__(self): return 7
        def __eq__(self, o):
            other.clear(); other.update(f"x{i}" for i in range(200)); return False
    S.add(7)
    other = set(range(64)); other.add(7)
    S2 = set(range(2000)); S2.add(Evil())
    # make `other` the iterated one
    return S2.difference_update(other)

# 3) symmetric_difference_update set path: add-during-iterate
def t_symdiff():
    other = set(range(64))
    class Evil:
        def __hash__(self): return 7
        def __eq__(self, o):
            other.clear(); other.update(range(500,900)); return False
    other.add(7)
    so = set(range(2000)); so.add(Evil())
    return so.symmetric_difference_update(other)

# 4) isdisjoint
def t_isdisjoint():
    other = set(range(64))
    class Evil:
        def __hash__(self): return 7
        def __eq__(self, o):
            other.clear(); other.update(range(500,900)); return False
    other.add(7)
    so = set(range(2000)); so.add(Evil())
    return so.isdisjoint(other)

run("intersection", t_intersection)
run("difference_update", t_diff_update)
run("symmetric_difference_update", t_symdiff)
run("isdisjoint", t_isdisjoint)
print("DONE")

ARMED=False
class E:
    def __init__(s,v): s.v=v
    def __hash__(s): return 1
    def __eq__(s,o):
        if ARMED:
            for g in (A,B):
                try: g.clear()
                except: pass
        return s.v==getattr(o,'v',None)
def mk():
    return set(E(i) for i in range(30)), set(E(i) for i in range(15,45))
ops = [
 ("and", lambda a,b: a & b),
 ("iand", lambda a,b: a.__iand__(b)),
 ("ior", lambda a,b: a.__ior__(b)),
 ("isub", lambda a,b: a.__isub__(b)),
 ("ixor", lambda a,b: a.__ixor__(b)),
 ("diffupd", lambda a,b: a.difference_update(b)),
 ("interupd", lambda a,b: a.intersection_update(b)),
 ("symupd", lambda a,b: a.symmetric_difference_update(b)),
 ("issub", lambda a,b: a.issubset(b)),
]
for name, fn in ops:
    A,B = mk(); ARMED=True
    try:
        fn(A,B); print(name, "ok")
    except Exception as e:
        print(name, "exc", type(e).__name__)
    ARMED=False

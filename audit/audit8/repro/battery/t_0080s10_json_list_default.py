# 0080 S10: _json C encoder list path (encoder_listencode_list) borrowed item across default.
import json

class Marker:
    lst = None
    def __init__(self, i): self.i = i

def default(o):
    # mutate the list being encoded while a borrowed item pointer is held
    if Marker.lst is not None:
        try: Marker.lst.clear()
        except Exception: pass
        try: Marker.lst.extend(range(3000))
        except Exception: pass
    return o.i

lst = []
Marker.lst = lst
lst.extend([Marker(i) for i in range(3000)])
try:
    s = json.dumps(lst, default=default)
    print("A encoded len:", len(s))
except Exception as ex:
    print("A raised:", type(ex).__name__, ex)

# also try a tuple path and a nested list with default
lst2 = []
Marker.lst = lst2
inner = [Marker(i) for i in range(100)]
lst2.extend(inner)
try:
    s = json.dumps([lst2, lst2], default=default)
    print("B encoded len:", len(s))
except Exception as ex:
    print("B raised:", type(ex).__name__, ex)
print("0080s10 done")

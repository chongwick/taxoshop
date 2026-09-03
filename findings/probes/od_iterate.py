from collections import OrderedDict

class K:
    def __hash__(self): return 1        # force hash collision
    def __eq__(self, other):
        od.clear()                       # free keys/nodes during the lookup
        return False

od = OrderedDict()
od[K()] = 0
od[K()] = 1                              # second colliding key -> real __eq__ during find_node
for k in od:                            # odictiter_iternext -> _odict_find_node -> __eq__ -> clear
    pass
print("no crash")

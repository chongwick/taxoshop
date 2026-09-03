from collections import OrderedDict

class K:
    def __hash__(self): return 1
    def __eq__(self, other):
        od.clear()      # free all nodes + od_fast_nodes during the lookup
        return True

od = OrderedDict()
od[K()] = 0            # stored key with hash 1
od[object()] = 1       # make it non-trivial / non-empty
od.move_to_end(K())    # reentrant __eq__ clears od mid-lookup
print("no crash")


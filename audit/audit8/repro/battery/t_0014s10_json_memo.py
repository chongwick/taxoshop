# 0014 S10 / 0091 S5: _json scanner _parse_object_unicode borrowed rval/pairs/memo across
# object_pairs_hook / object_hook / key __eq__/__hash__.
import json

captured = []

def pairs_hook(pairs):
    # stash and mutate: reach back at prior captured pairs lists
    captured.append(pairs)
    for p in captured[:-1]:
        try: p.clear()
        except Exception: pass
    return pairs

nested = '{"a": {"b": {"c": {"d": 1, "e": 2}, "f": 3}, "g": 4}, "h": 5}'
try:
    r = json.loads(nested, object_pairs_hook=pairs_hook)
    print("A parsed:", r)
except Exception as ex:
    print("A raised:", type(ex).__name__, ex)

# object_hook variant that mutates a shared dict
shared = {}
def obj_hook(d):
    shared.update(d)
    shared.clear()
    return d
try:
    r = json.loads(nested, object_hook=obj_hook)
    print("B parsed:", r)
except Exception as ex:
    print("B raised:", type(ex).__name__, ex)

# evil key class whose __eq__/__hash__ during memo interning mutates — keys are strings in JSON,
# so memo interning uses str keys; force many duplicate keys to exercise memo
big = "{" + ",".join(f'"k{i%8}": {i}' for i in range(2000)) + "}"
try:
    r = json.loads(big)
    print("C parsed keys:", len(r))
except Exception as ex:
    print("C raised:", type(ex).__name__, ex)
print("0014s10 done")

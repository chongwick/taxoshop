# 0014 S7: type_new set_names loop over borrowed tp_dict mutated by __set_name__
class Desc:
    def __init__(self, tag): self.tag = tag
    def __set_name__(self, owner, name):
        # mutate the owner's class dict during the set-names pass
        try:
            for i in range(200):
                setattr(owner, f"injected_{self.tag}_{i}", i)
            # also delete sibling descriptors
            for k in list(owner.__dict__):
                if k.startswith("d_") and k != name:
                    try: delattr(owner, k)
                    except Exception: pass
        except Exception as e:
            print("setname-exc", e)

def make():
    ns = {f"d_{i}": Desc(i) for i in range(100)}
    return type("C", (), ns)

try:
    C = make()
    print("made", len([k for k in C.__dict__]))
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s7")

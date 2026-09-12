d = {i:i for i in range(50)}
class EvilKey:
    def __hash__(self):
        d.clear()
        return 1
    def __eq__(self, o): return False
d2 = {EvilKey(): 1}
d.update(d2)
print("dict_update ok")

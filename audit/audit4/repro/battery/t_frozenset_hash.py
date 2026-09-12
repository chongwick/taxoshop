class E:
    def __hash__(s):
        return 1
    def __eq__(s,o): return False
fs = frozenset(E() for _ in range(20))
print("fs", len(fs))
d = {fs: 1}
print("frozenset ok")

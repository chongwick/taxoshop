from collections import Counter
c = Counter()
class E:
    def __hash__(self): return 5
    def __eq__(self, o): return self is o
    def __add__(self, other):
        # runs during PyNumber_Add(oldval, one); drop mapping ref to oldval
        c.clear()
        return 0
key = E()
c[key] = E()          # oldval is an E() with custom __add__
# update() -> _count_elements over [key]; oldval.__add__ runs, clears c
c.update([key])
print("no crash")

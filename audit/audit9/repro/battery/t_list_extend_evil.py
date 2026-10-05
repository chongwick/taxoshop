# list.extend with an iterator whose __next__ mutates the list being extended
lst = [0]*3
class It:
    def __init__(self): self.i=0
    def __iter__(self): return self
    def __next__(self):
        self.i += 1
        if self.i > 5: raise StopIteration
        lst.clear()
        return self.i
lst.extend(It())
print(lst)

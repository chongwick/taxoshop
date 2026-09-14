lst = list(range(20))
def gen():
    yield 1
    lst.clear()
    for i in range(100): yield i
lst[2:5] = gen()
print("list_slice ok", len(lst))

import itertools
# accumulate with evil binop that mutates nothing shared but returns weird
data=list(range(50))
def binop(a,b):
    data.clear()
    return a+b
print(list(itertools.accumulate(data, binop))[:3] if data else "empty")
# starmap over evil
def gen():
    yield (1,2)
    yield (3,4)
print(list(itertools.starmap(lambda x,y:x+y, gen())))
print("itertools ok")

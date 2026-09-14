import array
a = array.array('i', [0]*100)
def gen():
    yield 1
    a.__init__('i',[])  # reinit mid-extend
    for i in range(1000): yield i
try:
    a.extend(gen())
except Exception as e:
    print("exc", type(e).__name__)
print("array_extend ok", len(a))

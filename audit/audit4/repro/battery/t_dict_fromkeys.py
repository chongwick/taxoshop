target = dict.fromkeys(range(5))
def gen():
    yield 1
    yield 2
    raise StopIteration if False else ValueError("x")
# fromkeys with evil hash
class EvilK:
    n=[0]
    def __hash__(self):
        return 1
    def __eq__(self,o):
        return False
d = dict.fromkeys([EvilK() for _ in range(30)], 0)
print("dict_fromkeys ok", len(d))

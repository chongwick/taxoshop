import json
class Evil:
    pass
data = [Evil() for _ in range(5)]
def default(o):
    data.clear()   # clear the list being encoded
    return None
try:
    print(json.dumps(data, default=default))
except Exception as e:
    print("EXC", type(e).__name__)
print("done")

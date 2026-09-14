# 0080 S9: _json encoder dict path: default() mutates the dict being encoded
import json
d = {}
armed=[False]; junk=[]
class Bad:
    pass
def default(o):
    if armed[0]:
        armed[0]=False
        d.clear()
        for _ in range(200): junk.append({i:i for i in range(50)})
        del junk[:]
    return "ok"
d = {str(i): Bad() for i in range(80)}
armed[0]=True
try:
    print(len(json.dumps(d, default=default)))
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s9")

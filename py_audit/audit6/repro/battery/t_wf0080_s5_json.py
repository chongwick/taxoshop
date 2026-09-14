# wf0080 Site 5: json C scanner with object_hook & evil str subclass keys
import json
class EvilStr(str):
    def __eq__(self, other):
        return str.__eq__(self, other)
    __hash__ = str.__hash__
def hook(d):
    return d
dec = json.JSONDecoder(object_hook=hook)
try:
    r = dec.decode('{"a":1,"a":2,"b":3,"a":4}')
    print("json ->", r)
except Exception as e:
    print("json", type(e).__name__, e)
print("json done")

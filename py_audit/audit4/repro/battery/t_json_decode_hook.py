import json
holder={}
def oh(d):
    holder.setdefault('acc',[]).append(d)
    holder['acc'].clear()
    return d
s='{"a":{"b":{"c":[1,2,{"d":3}]}}, "e":[{"f":4},{"g":5}]}'*1
print(json.loads(s, object_hook=oh))
print("json_decode ok")

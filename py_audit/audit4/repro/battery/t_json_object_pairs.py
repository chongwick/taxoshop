import json
d = {}
class Evil:
    def __call__(self, pairs):
        return dict(pairs)
# object_pairs_hook mutating during decode
s = '{"a": 1, "b": [1,2,3], "c": {"d": 4}}'
def hook(pairs):
    return dict(pairs)
print(json.loads(s, object_pairs_hook=hook))
print("json_pairs ok")

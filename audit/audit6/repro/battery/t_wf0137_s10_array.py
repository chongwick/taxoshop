# wf0137 Site 10: array_ass_subscript index conversion frees ob_item
import array
arr = array.array('i', range(100))
class EvilIndex:
    def __index__(self):
        del arr[:]        # free/realloc ob_item
        arr.extend(range(2))
        return 0
try:
    arr[EvilIndex()] = 0
    print("array set ok, len", len(arr))
except Exception as e:
    print("array", type(e).__name__, e)
print("array done")

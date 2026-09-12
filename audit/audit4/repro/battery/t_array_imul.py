import array
a = array.array('i', [1,2,3])
class Evil:
    def __index__(self):
        a.__init__('i', [])   # try to clear/reinit during repeat count conv
        return 3
try:
    a *= Evil()
except Exception as e:
    print("exc", type(e).__name__)
print("array_imul ok", len(a))

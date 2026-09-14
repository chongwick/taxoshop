# 0014 S9: super_getattro walks borrowed tp_mro across descriptor __get__ that mutates __bases__
class B1:
    pass
class B2:
    pass

class Desc:
    def __get__(self, obj, objtype=None):
        # mutate bases of the type whose mro is being walked -> frees old tp_mro
        try:
            C.__bases__ = (B2,)
        except Exception as e:
            print("bases-exc", e)
        return 42

class Mid(B1):
    attr = Desc()

class C(Mid):
    def go(self):
        return super().attr

try:
    print(C().go())
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s9")

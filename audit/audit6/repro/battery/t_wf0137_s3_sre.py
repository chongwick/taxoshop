# wf0137 Site 3: match.__getitem__ index conversion running user code
import re
m = re.match(r"(a)(b)(c)", "abc")
class EvilIndex:
    def __index__(self):
        # try to invalidate the match's subject string binding
        return 1
try:
    print("group ->", m[EvilIndex()])
except Exception as e:
    print("sre", type(e).__name__, e)
print("sre done")

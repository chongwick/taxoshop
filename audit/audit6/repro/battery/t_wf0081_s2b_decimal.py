import decimal
ctxs = []
class EvilFlagVal:
    def __bool__(self):
        # deallocate the context during flags assignment/comparison
        ctxs.clear()
        return True
ctx = decimal.Context()
ctxs.append(ctx)
try:
    # trigger comparison/assignment path that consults truthiness re-entrantly
    ctx.flags[decimal.Inexact] = EvilFlagVal()
    del ctx
    print("decimal ok")
except Exception as e:
    print("decimal", type(e).__name__, e)
print("decimal done")

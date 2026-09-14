# 0014 S8: generator gi_frame across close() finalizer that re-enters
def gen():
    try:
        yield 1
        yield 2
    finally:
        try:
            g.send(None)   # re-enter during GeneratorExit finalization
        except Exception as e:
            print("reenter-exc", type(e).__name__, e)
g = gen()
next(g)
try:
    g.close()
except Exception as e:
    print("close-exc", type(e).__name__, e)
print("survived s8")

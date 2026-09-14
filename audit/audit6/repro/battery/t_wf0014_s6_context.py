# wf0014 Site 6: Context.run borrowed context after reentrant replace
import contextvars
ctx = contextvars.copy_context()
cv = contextvars.ContextVar("cv", default=0)
def fn():
    # enter another context / drop refs during run
    other = contextvars.copy_context()
    def inner(): cv.set(99)
    other.run(inner)
    return cv.get()
try:
    print("context ->", ctx.run(fn))
except Exception as e:
    print("context", type(e).__name__, e)
print("context done")

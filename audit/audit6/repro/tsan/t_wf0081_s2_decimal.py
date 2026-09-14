import decimal, threading
ctx = decimal.Context()
a = decimal.Decimal("1.123456789")
b = decimal.Decimal("3")
def f():
    for _ in range(100000):
        ctx.divide(a, b)   # sets Inexact/Rounded flags -> ctx->status |= ...
ts = [threading.Thread(target=f) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("decimal done", dict(ctx.flags))

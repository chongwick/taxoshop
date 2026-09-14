# 0077 S2: locale.localeconv() static lconv vs setlocale
import locale, threading
try: locale.setlocale(locale.LC_ALL, "C")
except Exception: pass
N=8; ITERS=5000
barrier=threading.Barrier(N)
def reader():
    barrier.wait()
    for _ in range(ITERS):
        d=locale.localeconv()
        _=d.get('decimal_point'); _=d.get('grouping')
def setter():
    barrier.wait()
    for i in range(ITERS):
        try: locale.setlocale(locale.LC_ALL, "C" if i&1 else "C.UTF-8")
        except Exception: pass
ts=[threading.Thread(target=reader) for _ in range(N//2)]+[threading.Thread(target=setter) for _ in range(N//2)]
[t.start() for t in ts]; [t.join() for t in ts]
print("done localeconv")

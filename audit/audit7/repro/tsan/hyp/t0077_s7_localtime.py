# 0077 S7: time.localtime/gmtime static struct tm reuse
import time, threading
N=8; ITERS=8000
barrier=threading.Barrier(N)
def w(g):
    barrier.wait()
    for _ in range(ITERS):
        (time.gmtime if g else time.localtime)()
ts=[threading.Thread(target=w,args=(i&1,)) for i in range(N)]
[t.start() for t in ts]; [t.join() for t in ts]
print("done localtime")

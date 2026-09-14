# 0077 S1: time.tzset writes process-global tzname vs localtime/strftime readers
import time, os, threading
N=8; ITERS=5000
barrier=threading.Barrier(N)
def setter():
    barrier.wait()
    for i in range(ITERS):
        os.environ['TZ']='UTC0' if i&1 else 'EST5EDT'
        time.tzset()
def reader():
    barrier.wait()
    for _ in range(ITERS):
        time.localtime(); 
        try: time.strftime('%Z')
        except Exception: pass
ts=[threading.Thread(target=setter) for _ in range(N//2)]+[threading.Thread(target=reader) for _ in range(N//2)]
[t.start() for t in ts]; [t.join() for t in ts]
print("done tzset")

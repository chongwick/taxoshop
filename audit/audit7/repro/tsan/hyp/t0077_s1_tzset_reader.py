# 0077 S1 (sharpened): ONE writer thread does tzset(); READER threads only read local time.
# Goal: show an innocent time.localtime()/strftime reader races the tzset writer.
import time, os, threading
stop=[False]
def writer():
    i=0
    while not stop[0]:
        os.environ['TZ']='UTC0' if i&1 else 'EST5EDT'
        time.tzset(); i+=1
def reader():
    for _ in range(20000):
        tm=time.localtime()
        try: s=time.strftime('%Z', tm)
        except Exception: pass
w=threading.Thread(target=writer); w.start()
rs=[threading.Thread(target=reader) for _ in range(6)]
[r.start() for r in rs]; [r.join() for r in rs]
stop[0]=True; w.join()
print("done tzset-reader")

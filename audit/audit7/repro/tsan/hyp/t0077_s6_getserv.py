# 0077 S6: socket.getservbyname/getprotobyname libc static servent/protoent
import socket, threading
N=8; ITERS=5000
barrier=threading.Barrier(N)
def w(kind):
    barrier.wait()
    for _ in range(ITERS):
        try:
            if kind: socket.getservbyname("http")
            else: socket.getprotobyname("tcp")
        except Exception: pass
ts=[threading.Thread(target=w,args=(i&1,)) for i in range(N)]
[t.start() for t in ts]; [t.join() for t in ts]
print("done getserv")

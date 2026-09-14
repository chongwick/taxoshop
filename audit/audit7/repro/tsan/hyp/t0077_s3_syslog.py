# 0077 S3: syslog module globals S_ident_o / S_log_open raced by openlog/syslog/closelog
import syslog, threading
N=8; ITERS=3000
barrier=threading.Barrier(N)
def worker(tag):
    barrier.wait()
    for i in range(ITERS):
        try:
            syslog.openlog(f"tag{tag}")
            syslog.syslog(syslog.LOG_INFO, "x")
            syslog.closelog()
        except Exception:
            pass
ts=[threading.Thread(target=worker,args=(i,)) for i in range(N)]
[t.start() for t in ts]; [t.join() for t in ts]
print("done syslog")

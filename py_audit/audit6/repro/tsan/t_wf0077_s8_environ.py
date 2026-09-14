import os, threading
def putter():
    for i in range(50000): os.environ["AUDITK"] = "v%d" % (i % 100)
def getter():
    for _ in range(50000):
        try: _ = os.environ.get("AUDITK"); _ = os.getenv("PATH")
        except Exception: pass
ts = [threading.Thread(target=putter), threading.Thread(target=getter),
      threading.Thread(target=putter), threading.Thread(target=getter)]
for t in ts: t.start()
for t in ts: t.join()
print("environ done")

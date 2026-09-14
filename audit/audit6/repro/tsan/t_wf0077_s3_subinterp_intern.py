import _interpreters as I, threading
code = '''
s = "".join(["zx%d" % k for k in range(50)])
import sys
for _ in range(2000):
    x = sys.intern("novelstring_" + s[:10])
'''
def run():
    sub = I.create()
    try: I.run_string(sub, code)
    finally:
        try: I.destroy(sub)
        except Exception: pass
ts = [threading.Thread(target=run) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("subinterp intern done")

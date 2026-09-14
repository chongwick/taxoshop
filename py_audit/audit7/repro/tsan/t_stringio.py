import io, threading
s = io.StringIO()
def w():
    for _ in range(100000): s.write("abcd")
def r():
    for _ in range(100000):
        try: s.getvalue(); s.seek(0); s.read(4)
        except Exception: pass
ts=[threading.Thread(target=w),threading.Thread(target=r),threading.Thread(target=w),threading.Thread(target=r)]
for t in ts:t.start()
for t in ts:t.join()
print("stringio done")

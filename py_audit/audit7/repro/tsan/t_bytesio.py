import io, threading
b = io.BytesIO()
def w():
    for _ in range(100000): b.write(b"abcd")
def r():
    for _ in range(100000):
        try: b.getvalue(); b.seek(0); b.read(4)
        except Exception: pass
ts=[threading.Thread(target=w),threading.Thread(target=r),threading.Thread(target=w),threading.Thread(target=r)]
for t in ts:t.start()
for t in ts:t.join()
print("bytesio done")

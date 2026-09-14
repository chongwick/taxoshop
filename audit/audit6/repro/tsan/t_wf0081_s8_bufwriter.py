import io, threading
raw = io.BytesIO()
bw = io.BufferedWriter(raw, buffer_size=4096)
def f():
    for _ in range(20000):
        try: bw.write(b"abcd")
        except Exception: break
ts = [threading.Thread(target=f) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("bufwriter done")

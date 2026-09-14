import locale, threading
try: locale.setlocale(locale.LC_ALL, "C")
except Exception: pass
def f():
    for _ in range(20000):
        try:
            locale.setlocale(locale.LC_ALL, "C")
            _ = locale.setlocale(locale.LC_CTYPE)  # reads static buffer
        except Exception: pass
ts = [threading.Thread(target=f) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("setlocale done")

# 0077 S8: faulthandler process-global thread/fatal_error state raced by concurrent
# dump_traceback_later / cancel_dump_traceback_later / enable / disable.
import faulthandler, threading, os, sys

# dump to devnull so we don't spam
devnull = open(os.devnull, "w")
stop = threading.Event()

def rearm():
    while not stop.is_set():
        try:
            faulthandler.dump_traceback_later(0.0005, repeat=True, file=devnull)
        except Exception:
            pass

def cancel():
    while not stop.is_set():
        faulthandler.cancel_dump_traceback_later()

def toggle():
    while not stop.is_set():
        try:
            faulthandler.enable(file=devnull)
            faulthandler.disable()
        except Exception:
            pass

ts = [threading.Thread(target=rearm) for _ in range(2)]
ts += [threading.Thread(target=cancel) for _ in range(2)]
ts += [threading.Thread(target=toggle) for _ in range(2)]
for t in ts: t.start()
import time
t0 = time.time()
while time.time() - t0 < 3.0:
    time.sleep(0.01)
stop.set()
for t in ts: t.join()
faulthandler.cancel_dump_traceback_later()
print("0077s8 faulthandler done")

# Minimal: two documented faulthandler APIs raced from two threads.
# Thread A loops dump_traceback_later; Thread B loops cancel_dump_traceback_later.
import faulthandler, threading, os, time

devnull = open(os.devnull, "w")
stop = threading.Event()

def rearm():
    while not stop.is_set():
        try:
            faulthandler.dump_traceback_later(0.001, file=devnull)
        except Exception:
            pass

def cancel():
    while not stop.is_set():
        faulthandler.cancel_dump_traceback_later()

a = threading.Thread(target=rearm)
b = threading.Thread(target=cancel)
a.start(); b.start()
t0 = time.time()
while time.time() - t0 < 5.0 and a.is_alive() and b.is_alive():
    time.sleep(0.01)
stop.set()
a.join(); b.join()
faulthandler.cancel_dump_traceback_later()
print("fh_min done")

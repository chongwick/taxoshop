import warnings, threading
stop = False
def warner():
    while not stop:
        with warnings.catch_warnings():
            warnings.warn("x", UserWarning)
def mutator():
    for _ in range(20000):
        warnings.filterwarnings("ignore")
        warnings.resetwarnings()
w = threading.Thread(target=warner); w.start()
m = threading.Thread(target=mutator); m.start()
m.join(); stop = True; w.join()
print("warnings done")

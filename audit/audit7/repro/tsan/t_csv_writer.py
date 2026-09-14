import csv, io, threading
out=io.StringIO(); w=csv.writer(out)
def f():
    for _ in range(50000):
        try: w.writerow([1,2,"three",4,5])
        except Exception: break
ts=[threading.Thread(target=f) for _ in range(4)]
for t in ts:t.start()
for t in ts:t.join()
print("csv_writer done")

# csv.writer.writerow borrows fields from PySequence_Fast; a field's __str__/
# __index__ could mutate the row list during quoting.
import csv, io
row = []
class Evil:
    def __str__(self):
        row.clear(); row.append("x"*5000)
        return "e"
w = csv.writer(io.StringIO())
row.extend([Evil(), Evil(), Evil()])
try: w.writerow(row)
except Exception as e: print("exc", type(e).__name__)
print("OK sweep_csv")

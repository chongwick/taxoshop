import csv, io
# evil sequence: __len__/iteration mutates? csv writerow takes an iterable
class EvilList(list):
    pass
w = csv.writer(io.StringIO())
row = ["a","b","c"]
class Evil:
    def __str__(self):
        row.clear(); row.append("x"*10000)
        return "z"
w.writerow([Evil(), Evil(), Evil()])
print("csv_writerow ok")

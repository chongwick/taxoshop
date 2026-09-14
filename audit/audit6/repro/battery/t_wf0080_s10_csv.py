# wf0080 Site 10: csv writer field __str__ rebinds dialect mid-join
import csv, io
w = None
class EvilStr:
    def __str__(self):
        # try to mutate writer dialect during writerow
        try: w.dialect = csv.excel
        except Exception as e: pass
        return "x" * 10
out = io.StringIO()
w = csv.writer(out, lineterminator="\r\n")
try:
    w.writerow([EvilStr(), EvilStr(), EvilStr()])
    print("csv ok:", repr(out.getvalue()))
except Exception as e:
    print("csv", type(e).__name__, e)
print("csv done")

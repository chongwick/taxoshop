# wf0080 Site 2: sqlite converter/text_factory reentrancy closes connection mid cast-map
import sqlite3
con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
def evil_conv(b):
    con.close()
    return b
sqlite3.register_converter("EVIL", evil_conv)
con.execute("CREATE TABLE t(a EVIL, b EVIL)")
con.execute("INSERT INTO t VALUES (1, 2)")
try:
    cur = con.execute("SELECT a, b FROM t")
    print("rows:", cur.fetchall())
except Exception as e:
    print("sqlite", type(e).__name__, e)
print("sqlite done")

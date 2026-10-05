# collation callback closes the connection during ORDER BY sort
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("create table t(x)")
con.executemany("insert into t values(?)", [(str(i),) for i in range(200)])

state = {"n": 0}
def myc(a, b):
    state["n"] += 1
    if state["n"] == 5:
        try:
            con.close()
        except Exception:
            pass
    return (a > b) - (a < b)

con.create_collation("myc", myc)
try:
    cur = con.execute("select x from t order by x collate myc")
    print("rows", len(cur.fetchall()))
except Exception as e:
    print("EXC", type(e).__name__, e)
print("done")

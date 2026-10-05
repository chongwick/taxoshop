# progress handler closes the connection mid-execute (connection->db path)
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("create table t(x)")
con.executemany("insert into t values(?)", [(i,) for i in range(500)])

def prog():
    try:
        con.close()
    except Exception:
        pass
    return 0

con.set_progress_handler(prog, 1)
try:
    cur = con.execute("select x from t order by x")
    print("rows", len(cur.fetchall()))
except Exception as e:
    print("EXC", type(e).__name__, e)
print("done")

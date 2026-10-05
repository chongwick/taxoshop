# aggregate step/finalize closes the connection during execute
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("create table t(x)")
con.executemany("insert into t values(?)", [(i,) for i in range(100)])

class Agg:
    def __init__(self):
        self.n = 0
    def step(self, v):
        self.n += 1
        if self.n == 10:
            try:
                con.close()
            except Exception:
                pass
    def finalize(self):
        return self.n

con.create_aggregate("myagg", 1, Agg)
try:
    cur = con.execute("select myagg(x) from t")
    print("res", cur.fetchall())
except Exception as e:
    print("EXC", type(e).__name__, e)
print("done")

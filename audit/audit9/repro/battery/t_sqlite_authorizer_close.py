# authorizer callback closes the connection during prepare/step
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("create table t(x)")
con.executemany("insert into t values(?)", [(i,) for i in range(50)])

def auth(action, a1, a2, dbname, trigger):
    try:
        con.close()
    except Exception:
        pass
    return sqlite3.SQLITE_OK

con.set_authorizer(auth)
try:
    cur = con.execute("select x from t")
    print("rows", len(cur.fetchall()))
except Exception as e:
    print("EXC", type(e).__name__, e)
print("done")

# 0014 S5: sqlite3.Row.__getitem__(name) borrows description across name __eq__ that closes cursor
import sqlite3
con = sqlite3.connect(":memory:")
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("create table t(aaa, bbb, ccc)")
cur.execute("insert into t values (1,2,3)")
cur.execute("select * from t")
row = cur.fetchone()
class Evil(str):
    def __eq__(self, other):
        try:
            cur.close(); con.close()
        except Exception as e:
            print("close-exc", e)
        junk = [bytes(4096) for _ in range(50)]
        return str.__eq__(self, other)
    def __hash__(self): return hash(str(self))
try:
    print(row[Evil("ccc")])
except Exception as e:
    print("exc", type(e).__name__, e)
print("survived s5")

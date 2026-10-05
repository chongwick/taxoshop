# Target the UNGUARDED locked=0 window: iternext does self->locked=0 THEN stmt_step(stmt).
# execute() steps row 1 itself (locked=1). The row-2 step happens inside fetchall()->iternext
# with locked=0, so a UDF evaluated there can reenter cur.execute() with NO recursion guard:
# the reentrant execute SUCCEEDS, Py_XSETREF(self->statement, new) frees the old pysqlite_Statement
# whose sqlite3_stmt is still mid-step in the enclosing sqlite3_step -> use-after-free.
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE t(a)")
con.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(6)])
cur = con.cursor()

n = [0]
def myfunc(x):
    n[0] += 1
    # Skip the first call (that one runs inside execute(), locked=1 -> would raise).
    # Reenter on the SECOND call, which runs inside iternext's stmt_step with locked=0.
    if n[0] == 2:
        cur.execute("SELECT 1")   # UNGUARDED: swaps/frees self->statement mid-step
    return x

con.create_function("myfunc", 1, myfunc)
cur.execute("SELECT myfunc(a) FROM t")
print(cur.fetchall())
print("no crash")

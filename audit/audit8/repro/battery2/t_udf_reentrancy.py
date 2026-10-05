# HUNT: pysqlite_cursor_iternext sets self->locked=0 BEFORE stmt_step(stmt), and stmt_step ->
# sqlite3_step can invoke a user-defined function (arbitrary Python) UNGUARDED. execute() steps
# row 1 itself (locked=1), so the SECOND row's step happens in iternext with locked=0. A UDF that
# reenters cur.execute()/close() there runs while sqlite3_step is still executing on the local
# stmt -> statement reset/finalize under an active step, or self->statement swap/NULL.
import sqlite3

state = {}

def run(label, fn):
    con = sqlite3.connect(":memory:")
    con.create_function("myfunc", 1, fn)
    con.execute("CREATE TABLE t(a)")
    con.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(6)])
    cur = con.cursor()
    state["cur"] = cur
    state["con"] = con
    state["n"] = 0
    try:
        cur.execute("SELECT myfunc(a) FROM t")
        rows = cur.fetchall()
        print(f"  {label}: {rows} (no crash)")
    except Exception as ex:
        print(f"  {label}: raised {type(ex).__name__}: {ex}")

def fnA(x):
    state["n"] += 1
    try: state["cur"].execute("SELECT 1")
    except Exception: pass
    return x
run("A udf->cur.execute", fnA)

def fnB(x):
    try: state["cur"].close()
    except Exception: pass
    return x
run("B udf->cur.close", fnB)

def fnC(x):
    try: state["con"].close()
    except Exception: pass
    return x
run("C udf->con.close", fnC)

def fnD(x):
    try:
        c2 = state["con"].cursor(); c2.execute("SELECT 1"); c2.fetchall()
    except Exception: pass
    return x
run("D udf->other cursor", fnD)

print("udf_reentrancy done")

# HUNT: _pysqlite_fetch_one_row iterates columns calling text_factory / converter (arbitrary
# Python) while dereferencing self->statement->st on each iteration, holding no local ref to
# self->statement. A callback that closes the cursor (Py_CLEAR(self->statement)) or re-executes
# should make the next column deref hit NULL / freed memory.
import sqlite3, sys

def variant(label, evil_setup):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE t(a TEXT, b TEXT, c TEXT, d TEXT)")
    con.execute("INSERT INTO t VALUES ('col0','col1','col2','col3')")
    cur = con.cursor()
    evil_setup(con, cur)
    cur.execute("SELECT a, b, c, d FROM t")
    try:
        r = cur.fetchone()
        print(f"  {label}: fetched {r} (no crash)")
    except Exception as ex:
        print(f"  {label}: raised {type(ex).__name__}: {ex}")

# A: text_factory closes the cursor on first column
def setA(con, cur):
    calls = {"n": 0}
    def tf(b):
        calls["n"] += 1
        if calls["n"] == 1:
            cur.close()
        return bytes(b).decode()
    con.text_factory = tf
variant("A text_factory->cur.close", setA)

# B: text_factory closes the connection on first column
def setB(con, cur):
    calls = {"n": 0}
    def tf(b):
        calls["n"] += 1
        if calls["n"] == 1:
            con.close()
        return bytes(b).decode()
    con.text_factory = tf
variant("B text_factory->con.close", setB)

# C: text_factory re-executes the cursor (replaces self->statement) on first column
def setC(con, cur):
    calls = {"n": 0}
    def tf(b):
        calls["n"] += 1
        if calls["n"] == 1:
            try: cur.execute("SELECT 1")
            except Exception: pass
        return bytes(b).decode()
    con.text_factory = tf
variant("C text_factory->cur.execute", setC)

print("sqlite_fetch_reentrancy done")

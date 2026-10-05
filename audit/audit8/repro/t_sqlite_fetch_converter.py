# Second vector for the same bug: a detect_types converter (instead of text_factory) that
# reenters cur.execute() mid-row and swallows the "Recursive use of cursors" exception.
# Crashes at Modules/_sqlite/cursor.c:383 (sqlite3_column_blob(self->statement->st, i)),
# self->statement == NULL. Pure Python, no ctypes.
import sqlite3

con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
con.execute("CREATE TABLE t(a evil, b evil)")
con.execute("INSERT INTO t VALUES (x'1234', x'5678')")
cur = con.cursor()

def conv(blob):
    try:
        cur.execute("SELECT 1")           # reentrant -> NULLs self->statement, then raises
    except sqlite3.ProgrammingError:
        pass                              # swallow "Recursive use of cursors not allowed."
    return blob

sqlite3.register_converter("evil", conv)
cur.execute("SELECT a, b FROM t")
print(cur.fetchone())
print("no crash")

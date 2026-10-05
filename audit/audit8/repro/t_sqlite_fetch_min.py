# NEW BUG: sqlite3 Cursor NULL-deref / statement corruption via reentrant execute() from a
# text_factory (or converter) callback whose "Recursive use of cursors not allowed" exception
# is swallowed.
#
# _pysqlite_query_execute() (Modules/_sqlite/cursor.c) sets self->locked=1 but its recursion
# guard (check_cursor_locked, reached only inside get_statement_from_cache) fires AFTER it has
# already stmt_reset()'d the outer statement and run Py_XSETREF(self->statement, NULL). So a
# reentrant execute() corrupts the cursor before raising. When the callback catches that
# exception and returns normally, _pysqlite_fetch_one_row keeps looping over the remaining
# columns and dereferences self->statement->st with self->statement == NULL.
#
# Pure Python, no ctypes. Crashes CPython (UBSan: null member access at cursor.c:402;
# SIGSEGV on a normal build).
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE t(a TEXT, b TEXT)")
con.execute("INSERT INTO t VALUES ('first', 'second')")

cur = con.cursor()

def evil_text_factory(data):
    # Runs while _pysqlite_fetch_one_row holds a borrowed self->statement.
    try:
        cur.execute("SELECT 1")   # reentrant: corrupts self->statement, then raises
    except sqlite3.ProgrammingError:
        pass                      # swallow "Recursive use of cursors not allowed."
    return bytes(data).decode()

con.text_factory = evil_text_factory
cur.execute("SELECT a, b FROM t")
print(cur.fetchone())            # column 'a' -> callback (NULLs self->statement);
                                 # column 'b' -> deref NULL self->statement -> crash
print("no crash")

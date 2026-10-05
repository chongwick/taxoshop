# FINDING-002 — NEW: sqlite3 Cursor NULL-deref via reentrant `execute()` inside a text_factory/converter during fetch

**Status:** CONFIRMED crash (ASan/UBSan + vanilla SIGSEGV) · **NEW** (distinct from open #143662
and #146471) · pure Python, **no ctypes**.
**Parent pattern:** workflow-0014 (borrowed/derived handle used after backing invalidation) —
`_pysqlite_fetch_one_row` holds a borrowed `self->statement` across a user-code callout that
NULLs it. Also touches workflow-0080 (callback re-entrancy invalidates borrowed state).
**Build:** `taxoshop/cpython-asan-ubsan:current`, CPython 3.16.0a0 HEAD `e5d4fa28`; also
confirmed a raw SIGSEGV (exit 139) on `cpython-vanilla:latest`.

## Summary
`_pysqlite_fetch_one_row` (Modules/_sqlite/cursor.c:343) builds a result row column-by-column,
invoking arbitrary Python per column — a registered **converter**
(`PyObject_CallOneArg(converter, item)`, :396) or the connection **text_factory**
(`PyObject_CallFunction(self->connection->text_factory, ...)`, :439) — while repeatedly
dereferencing `self->statement->st` for later columns. It holds **no local strong ref to
`self->statement`** and does not revalidate it after the callout.

If that callback re-enters `cur.execute(...)` on the **same** cursor, the reentrancy guard in
`_pysqlite_query_execute` fires **too late**: the function has already
```c
    self->locked = 1;                                  // cursor.c:810
    ...
    if (self->statement) { stmt_reset(self->statement); }   // resets the OUTER statement (:854)
    PyObject *stmt = get_statement_from_cache(self, operation); // -> check_cursor_locked (:500)
                                                                 //    sees locked==1 -> returns NULL
    Py_XSETREF(self->statement, (pysqlite_Statement *)stmt);    // self->statement = NULL (:861)
    if (!self->statement) { goto error; }              // raises "Recursive use of cursors..."
```
so by the time "Recursive use of cursors not allowed." is raised, `self->statement` is already
**NULL** (and the outer statement was reset / its last ref dropped). A caller that **swallows**
that `ProgrammingError` (an ordinary `try/except` in a text_factory/converter) returns normally;
the outer `_pysqlite_fetch_one_row` loop then reads `self->statement->st` for the next column
with `self->statement == NULL` → NULL member access → crash.

## Root cause
Two cooperating defects:
1. `_pysqlite_fetch_one_row` treats `self->statement` as stable across the text_factory/converter
   callout; it never re-checks it after user code runs.
2. `_pysqlite_query_execute`'s recursion guard is enforced only deep inside
   `get_statement_from_cache`, *after* it has already mutated cursor state
   (`stmt_reset(self->statement)` then `Py_XSETREF(self->statement, NULL)`), so a rejected
   reentrant `execute()` leaves the cursor in a NULL-statement state instead of being a no-op.

## Reproducers (pure Python, no ctypes)
- `repro/t_sqlite_fetch_min.py` — text_factory vector → crash at `cursor.c:402`
  (`sqlite3_column_type(self->statement->st, i)`).
- `repro/t_sqlite_fetch_converter.py` — detect_types converter vector → crash at `cursor.c:383`
  (`sqlite3_column_blob(self->statement->st, i)`).

Minimal (text_factory):
```python
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE t(a TEXT, b TEXT)")
con.execute("INSERT INTO t VALUES ('first', 'second')")
cur = con.cursor()
def evil_text_factory(data):
    try:
        cur.execute("SELECT 1")            # reentrant: NULLs self->statement, then raises
    except sqlite3.ProgrammingError:
        pass                               # swallow "Recursive use of cursors not allowed."
    return bytes(data).decode()
con.text_factory = evil_text_factory
cur.execute("SELECT a, b FROM t")
print(cur.fetchone())                      # column 'a' -> callback -> NULL; column 'b' -> crash
```

## Sanitizer output
`logs/sqlite_fetch.asan.txt` (text_factory vector):
```
Modules/_sqlite/cursor.c:402:23: runtime error: member access within null pointer of type 'struct pysqlite_Statement'
    #0 _pysqlite_fetch_one_row Modules/_sqlite/cursor.c:402
    #1 pysqlite_cursor_iternext Modules/_sqlite/cursor.c:1155
    #2 pysqlite_cursor_fetchone_impl Modules/_sqlite/cursor.c:1206
    #3 pysqlite_cursor_fetchone Modules/_sqlite/clinic/cursor.c.h:169
```
`logs/sqlite_fetch_converter.asan.txt` (converter vector):
```
Modules/_sqlite/cursor.c:383:32: runtime error: member access within null pointer of type 'struct pysqlite_Statement'
    #0 _pysqlite_fetch_one_row Modules/_sqlite/cursor.c:383
    #1 pysqlite_cursor_iternext Modules/_sqlite/cursor.c:1155
```
`logs/sqlite_fetch_vanilla.segv.txt` — vanilla (non-sanitizer) `cpython-vanilla:latest` build:
`Segmentation fault` (exit 139), confirming a real crash, not a UBSan-only artifact.

## Duplicate analysis — NEW (distinct from the open sqlite3 crashers)
- **#143662 (OPEN)** "Null pointer dereference in `cursor.fetchone` after re-entrant
  `text_factory` closes connection" — DISTINCT: its trigger is `Connection.close()`, the cleared
  field is `self->connection->db`, the crash is in `pysqlite_cursor_iternext` at
  `sqlite3_changes(db)` (inside libsqlite3) and requires a **DML/RETURNING** statement. My bug's
  trigger is reentrant `execute()`, the cleared field is `self->statement`, the crash is **inside
  `_pysqlite_fetch_one_row`** (cursor.c:383/402, CPython code) on an ordinary multi-column SELECT
  — a different code path, faulting pointer, and crash site. (Same broad theme: fetch_one_row does
  not revalidate state after the callout; a close-path-only fix would not cover the
  execute-path `self->statement` NULLing.) Verified `con.close()` inside text_factory does NOT
  crash my SELECT repro (no `is_dml`), confirming the paths are separate.
- **#146471 (OPEN)** "Segfault from sqlite3 module when abusing threads" — DISTINCT: multithread
  data race; my bug is single-threaded reentrancy.
- `git log -8000` on HEAD `e5d4fa28`: no fix for text_factory/converter fetch reentrancy or
  `Recursive use of cursors` state corruption.

## Suggested fix direction (for the report, not applied here)
Make `_pysqlite_query_execute` enforce `check_cursor_locked(self)` at the **top** (before any
`stmt_reset`/`Py_XSETREF`), as `cursor.close()`/`executemany` already do (cursor.c:115/1330);
and/or have `_pysqlite_fetch_one_row` re-check `self->statement != NULL` after each
text_factory/converter callout and raise cleanly instead of dereferencing.

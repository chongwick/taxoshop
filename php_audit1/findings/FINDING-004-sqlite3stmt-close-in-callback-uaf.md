# FINDING-004 — `SQLite3Stmt::close()` from inside a callback frees the running statement (UAF / SEGV)

**Status:** CONFIRMED (SEGV under ASan), APPARENTLY NOVEL. Immediate sibling of just-merged
**GH-23650** (`7300fa520dd`, "ext/sqlite3: reject close() from inside a callback") which the
fix did **not** cover.

**Extension:** ext/sqlite3 (bundled builds too; here system `libsqlite3.so`).
**Macro-taxo:** workflow-0137 / workflow-0080 — reentrant user code invalidates native state
still in use (same family as GH-23650).
**Build:** `taxoshop/php-asan-ubsan:current`, PHP 8.6.0-dev ZTS DEBUG @ HEAD `938a3110bf3`.

## Root cause

GH-23650 added a per-**database** re-entry counter `db_obj->in_callback`, incremented around
every userland callback (`sqlite3_do_callback` sqlite3.c:769-822, collation :943-954, authorizer
:2269-2275). But it is **only checked in `PHP_METHOD(SQLite3, close)`** (sqlite3.c:190):

```c
if (db_obj->in_callback) {
    zend_throw_error(NULL, "Cannot close SQLite3 database while inside a callback");
    RETURN_THROWS();
}
```

`PHP_METHOD(SQLite3Stmt, close)` (sqlite3.c:1454) has **no such guard**:

```c
zend_llist_del_element(&(stmt_obj->db_obj->free_list), stmt_obj,
                       (int (*)(void *, void *)) php_sqlite3_compare_stmt_free);
```

`zend_llist_del_element` runs the list dtor `php_sqlite3_free_list_dtor` (sqlite3.c:2306):

```c
static void php_sqlite3_free_list_dtor(void **item) {
    php_sqlite3_stmt *stmt_obj = *item;
    if (stmt_obj && stmt_obj->initialised) {
        sqlite3_finalize(stmt_obj->stmt);   // frees the VDBE
        stmt_obj->initialised = false;      // NOTE: stmt_obj->stmt left DANGLING
    }
}
```

`SQLite3Stmt::execute()` (sqlite3.c:1877) drives the statement with
`return_code = sqlite3_step(stmt_obj->stmt)` (**:1901**). During that `sqlite3_step`, sqlite3
evaluates the SQL — invoking any registered UDF / aggregate / collation callback into userland.
If that callback calls `$stmt->close()` on the very statement being stepped,
`sqlite3_finalize()` frees the active VDBE. Control returns into `sqlite3_step`, which keeps
using the freed VDBE → **use-after-free**. (Even if step returned, `execute()` immediately calls
`sqlite3_reset(stmt_obj->stmt)` at :1907 on the finalized/dangling pointer.)

Because the crash lands in the system `libsqlite3.so` (not ASan-instrumented) it surfaces as a
`DEADLYSIGNAL` SEGV rather than a clean `heap-use-after-free` report; it is nonetheless a
use-after-free (freed VDBE read).

## Repro (primary — UDF callback), `repro/battery6/e6_01_stmt_close_in_callback.php`

```php
<?php
$db = new SQLite3(':memory:');
$db->createFunction('evil', function () {
    global $stmt;
    $stmt->close();            // finalizes stmt_obj->stmt while sqlite3_step runs it
    return 1;
});
$stmt = $db->prepare("SELECT evil()");
$res = $stmt->execute();
```

ASan (`USE_ZEND_ALLOC=0`), exit 134:

```
==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000063 ... READ
    #0 sqlite3ApiExit  (libsqlite3.so.0+0x912b4)
    #1 sqlite3_step    (libsqlite3.so.0+0xe1fb0)
    #2 zim_SQLite3Stmt_execute  ext/sqlite3/sqlite3.c:1901:16
```

Log: `logs/finding-004-e6_01_stmt_close.asan.txt`.

## Trigger vectors / controls (all in `repro/battery6/`)

- `e6_01` — **UDF callback** calls `$stmt->close()` → **SEGV (exit 134)**.
- `e6_04` — **collation callback** calls `$stmt->close()` (ORDER BY ... COLLATE) → **SEGV**.
  Aggregate step/finalize is the same code path (also vulnerable).
- `e6_02` — control, callback does *not* close → clean, exit 0.
- `e6_03` — control, callback calls the **database** `$db->close()` → correctly throws
  "Cannot close SQLite3 database while inside a callback" (GH-23650 guard works), no crash.
- `e6_05` — `SQLite3Result::finalize()` from callback → benign (resets, does not finalize).

## Fix

Mirror GH-23650 at statement granularity: in `PHP_METHOD(SQLite3Stmt, close)` (and any path
reaching `php_sqlite3_free_list_dtor` / `sqlite3_finalize` on a live stmt — e.g. re-`prepare`
reuse), reject teardown while `stmt_obj->db_obj->in_callback != 0`:

```c
if (stmt_obj->db_obj->in_callback) {
    zend_throw_error(NULL, "Cannot close SQLite3 statement while inside a callback");
    RETURN_THROWS();
}
```

The existing per-db counter already covers all four callback kinds, so no new bookkeeping is
needed — only the missing check.

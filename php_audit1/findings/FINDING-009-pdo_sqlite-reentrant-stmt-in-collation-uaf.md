# FINDING-009 — pdo_sqlite: reentrant statement operation from inside a collation/UDF callback finalizes/resets the running VDBE → SEGV (memory-safety)

**Component:** `ext/pdo_sqlite` (PDO SQLite driver)
**Type:** Reentrancy → use-of-reset/finalized VDBE → SIGSEGV (jump to `0x0`). Same
family as wf-0137/wf-0080 (reentrant user code invalidates native state).
**Severity:** crash / memory-unsafety (control-flow lands at address 0). Reachable
from ordinary PHP with a userland collation or UDF.
**Status:** CONFIRMED on `php-src` HEAD `938a3110bf3` (8.6.0-dev), ASan build.
Apparently **NOVEL** — direct sibling of the just-merged GH-23650
(`7300fa520dd`, "ext/sqlite3: reject close() from inside a callback"), which added
the `in_callback` guard **only to `ext/sqlite3`**. `ext/pdo_sqlite` has **no
reentrancy guard of any kind** (`grep in_callback ext/pdo_sqlite` → nothing).

## Root cause

`ext/pdo_sqlite` registers userland callables as SQLite collations
(`sqliteCreateCollation` / `Pdo\Sqlite::createCollation`) and UDFs
(`sqliteCreateFunction`/`sqliteCreateAggregate`). SQLite invokes these callbacks
**synchronously from inside `sqlite3_step()` → `sqlite3VdbeExec()`** while the
statement's VDBE is actively running (for a collation: during the `ORDER BY`
sort comparison).

The collation callback runs arbitrary PHP (`php_sqlite3_collation_callback`,
`sqlite_driver.c:498` → `zend_call_known_fcc`, `:509`). From that PHP, the user
can call methods on the *same* `PDOStatement` that is currently being stepped:

* `PDOStatement::closeCursor()` → `pdo_sqlite_stmt_cursor_closer`
  (`sqlite_statement.c:375`) → `sqlite3_reset(S->stmt)` on the **running** VDBE.
* `PDOStatement::execute()` → `pdo_sqlite_stmt_execute` (`sqlite_statement.c:45`)
  → `sqlite3_reset(S->stmt)` then `sqlite3_step(S->stmt)` — reset + reentrant
  step of the VDBE already on the C stack.

`sqlite3_reset()` tears down the running sorter/VDBE cursor state. When the outer
`sqlite3VdbeExec()` resumes after the collation returns, it dereferences the
cleared state and jumps through a null pointer → SIGSEGV at PC `0x0`.

Nothing in `ext/pdo_sqlite` prevents this: there is no "in callback" / "statement
busy" flag consulted before `sqlite3_reset`/`sqlite3_finalize`/`sqlite3_step`.
(`sqlite3_stmt_busy()` is only used as a read-only attribute getter at
`sqlite_statement.c:398`, never as a guard.)

## Relationship to GH-23650 (the fix that missed this)

GH-23650 (`7300fa520dd`) added `db_obj->in_callback`, bumped around all four
callback kinds, and rejects `SQLite3::close()` while set — **in `ext/sqlite3`
only**. FINDING-004 (this audit) already showed `ext/sqlite3` `SQLite3Stmt::close()`
was left unguarded by that fix. FINDING-009 is the **`pdo_sqlite`** analogue:
`pdo_sqlite` never received *any* part of that hardening, so the entire
reenter-your-own-statement-from-a-callback surface is open — via the modern,
non-deprecated `Pdo\Sqlite::createCollation()` API.

Note `pdo_sqlite`'s connection *close* path is NOT the vector: `sqlite_handle_closer`
(`sqlite_driver.c:151`) uses `sqlite3_close_v2` (deferred/zombie close), so closing
the connection mid-callback is tolerated. The live sink is statement-level
`sqlite3_reset`/`sqlite3_step`/`sqlite3_finalize`, which act immediately.

## Minimal reproducer (`repro/battery7/e7_08_min.php`)

```php
<?php
$db = Pdo\Sqlite::connect('sqlite::memory:');
$db->exec("CREATE TABLE t(x TEXT)");
$db->exec("INSERT INTO t VALUES ('b'),('a'),('c'),('d'),('e')");

$stmt = null;
$db->createCollation('evil', function ($a, $b) use (&$stmt) {
    $stmt->closeCursor();          // sqlite3_reset() on the running sort VDBE
    return $a <=> $b;
});

$stmt = $db->prepare("SELECT x FROM t ORDER BY x COLLATE evil");
$stmt->execute();                  // SEGV inside sqlite3VdbeExec after the reset
```

Run:
```
USE_ZEND_ALLOC=0 ASAN_OPTIONS=detect_leaks=0:abort_on_error=1 \
  ./sapi/cli/php repro/battery7/e7_08_min.php
```

### Native backtrace (gdb, from `e7_06`, identical for `e7_05`/`e7_08`)
```
#0  0x0000000000000000 in ?? ()
#1  0x... in ?? () from /lib/.../libsqlite3.so.0
#2  0x... in ?? () from /lib/.../libsqlite3.so.0
#3  sqlite3VdbeExec () from libsqlite3.so.0
#4  sqlite3_step () from libsqlite3.so.0
#5  pdo_sqlite_stmt_execute (stmt=...) at ext/pdo_sqlite/sqlite_statement.c:54
#6  zim_PDOStatement_execute (...) at ext/pdo/pdo_stmt.c:456
...
```
The crash is the **outer** `execute()`'s `sqlite3_step` (frame #5, the sort);
the reentrant `closeCursor()`/`execute()` from the collation already returned,
having corrupted the VDBE. libsqlite3 is the system shared lib (not ASan-
instrumented), so ASan reports a bare `SEGV (<unknown module>)`; it is a genuine
use-of-freed/reset VDBE, not a clean error return.

## Variants tested (`repro/battery7/`)

* `e7_05_collation_execute.php` — collation → `$stmt->execute()` → **SEGV**.
* `e7_06_collation_closecursor.php` — collation → `$stmt->closeCursor()` → **SEGV**.
* `e7_08_min.php` — minimal, modern `Pdo\Sqlite`/`createCollation` API → **SEGV**.
* `e7_07_control_noreentry.php` — same sort + collation, no reentrancy → clean
  (sort completes, `done`). **Differential proves the reentrancy is the cause.**
* `e7_01_reentrant_execute.php` — scalar UDF `SELECT evil()` + reentrant
  `execute()` → PHP stack-overflow error (single-row re-fetch recurses), not the
  memory bug; the sort/collation path is the reliable memory-safety trigger.
* `e7_02..e7_04` — scalar-UDF `closeCursor`/GC-free variants → clean (trivial
  single-op VDBE survives a reset; sorter state does not).

Logs: `logs/finding-009-e7_06_collation_closecursor.asan.txt`,
`logs/finding-009-e7_08_min.asan.txt`.

## Suggested fix

Port the GH-23650 hardening to `ext/pdo_sqlite`: keep an `in_callback` counter on
`pdo_sqlite_db_handle`, increment it around every userland callout
(`do_callback`, `php_sqlite3_collation_callback`, authorizer), and reject
statement/connection teardown+re-step operations while it is non-zero — i.e. in
`pdo_sqlite_stmt_execute`, `pdo_sqlite_stmt_cursor_closer`, and the statement
dtor (throw / no-op instead of `sqlite3_reset`/`sqlite3_step`/`sqlite3_finalize`
on a statement whose step is on the stack). Alternatively guard with
`sqlite3_stmt_busy(S->stmt)`.

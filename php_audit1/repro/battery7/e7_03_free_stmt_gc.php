<?php
// Drop the only userland reference to the running statement from inside its own
// UDF, then force GC. If the statement object can be freed here,
// pdo_sqlite_stmt_dtor -> sqlite3_finalize() frees the VDBE mid-step (UAF).
$db = new PDO('sqlite::memory:');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$GLOBALS['stmt'] = null;
$db->sqliteCreateFunction('evil', function () {
    $GLOBALS['stmt'] = null;   // drop ref to the executing statement
    gc_collect_cycles();
    return 1;
});
$GLOBALS['stmt'] = $db->prepare("SELECT evil()");
$GLOBALS['stmt']->execute();
echo "done\n";

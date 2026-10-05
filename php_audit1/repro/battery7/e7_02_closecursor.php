<?php
// PDOStatement::closeCursor() from inside a UDF -> pdo_sqlite_stmt_cursor_closer
// -> sqlite3_reset(S->stmt) on the VDBE currently mid-step.
$db = new PDO('sqlite::memory:');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$stmt = null;
$db->sqliteCreateFunction('evil', function () use (&$stmt) {
    $stmt->closeCursor();   // sqlite3_reset on running VDBE
    return 1;
});
$stmt = $db->prepare("SELECT evil()");
$stmt->execute();
var_dump($stmt->fetchAll());
echo "done\n";

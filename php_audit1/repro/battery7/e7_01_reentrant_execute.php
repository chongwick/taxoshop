<?php
// Reentrant PDOStatement::execute() on the SAME statement from inside a UDF
// fired by that statement's own sqlite3_step(). Inner execute calls
// sqlite3_reset(S->stmt) then sqlite3_step(S->stmt) on the VDBE currently
// running on the C stack. pdo_sqlite has NO in_callback guard.
$db = new PDO('sqlite::memory:');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$stmt = null;
$db->sqliteCreateFunction('evil', function () use (&$stmt) {
    $stmt->execute();   // reentrant reset+step on the running VDBE
    return 1;
});
$stmt = $db->prepare("SELECT evil()");
$stmt->execute();
var_dump($stmt->fetchAll());
echo "done\n";

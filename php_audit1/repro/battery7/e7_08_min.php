<?php
// MINIMAL: pdo_sqlite has no reentrancy guard. A collation comparator runs as
// userland inside the sort's sqlite3_step()/VdbeExec(). Calling closeCursor()
// (-> sqlite3_reset) on that same statement resets the running sort VDBE; when
// VdbeExec resumes it dereferences cleared sorter state -> SEGV (jump to 0x0).
// Sibling of GH-23650 (which only guarded ext/sqlite3, via in_callback). No
// equivalent guard exists in ext/pdo_sqlite.
$db = Pdo\Sqlite::connect('sqlite::memory:');
$db->exec("CREATE TABLE t(x TEXT)");
$db->exec("INSERT INTO t VALUES ('b'),('a'),('c'),('d'),('e')");

$stmt = null;
$db->createCollation('evil', function ($a, $b) use (&$stmt) {
    $stmt->closeCursor();          // sqlite3_reset() on the running sort VDBE
    return $a <=> $b;
});

$stmt = $db->prepare("SELECT x FROM t ORDER BY x COLLATE evil");
$stmt->execute();
var_dump($stmt->fetchAll());
echo "done\n";

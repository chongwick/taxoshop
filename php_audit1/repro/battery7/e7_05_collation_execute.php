<?php
// Collation callback variant: reentrant execute() of the sorting statement from
// inside the collation comparator (php_sqlite3_collation_callback), which runs
// during that statement's own sqlite3_step (ORDER BY compare).
$db = new PDO('sqlite::memory:');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$db->exec("CREATE TABLE t(x TEXT)");
$db->exec("INSERT INTO t VALUES ('b'),('a'),('c')");
$stmt = null;
$db->sqliteCreateCollation('evil', function ($a, $b) use (&$stmt) {
    static $n = 0;
    if ($n++ === 0) { $stmt->execute(); }   // reentrant reset+step on running VDBE
    return strcmp($a, $b);
});
$stmt = $db->prepare("SELECT x FROM t ORDER BY x COLLATE evil");
$stmt->execute();
var_dump($stmt->fetchAll());
echo "done\n";

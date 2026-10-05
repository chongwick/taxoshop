<?php
// Collation callback -> closeCursor() (sqlite3_reset) on the running sort VDBE.
$db = new PDO('sqlite::memory:');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$db->exec("CREATE TABLE t(x TEXT)");
$db->exec("INSERT INTO t VALUES ('b'),('a'),('c'),('d'),('e')");
$stmt = null;
$db->sqliteCreateCollation('evil', function ($a, $b) use (&$stmt) {
    $stmt->closeCursor();
    return strcmp($a, $b);
});
$stmt = $db->prepare("SELECT x FROM t ORDER BY x COLLATE evil");
$stmt->execute();
var_dump($stmt->fetchAll());
echo "done\n";

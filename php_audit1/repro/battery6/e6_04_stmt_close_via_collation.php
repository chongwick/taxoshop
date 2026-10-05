<?php
$db = new SQLite3(':memory:');
$db->createCollation('EVILCOLL', function ($a, $b) {
    global $stmt;
    $stmt->close();
    return strcmp($a, $b);
});
$db->exec("CREATE TABLE t(x TEXT)");
$db->exec("INSERT INTO t VALUES ('b'),('a')");
$stmt = $db->prepare("SELECT x FROM t ORDER BY x COLLATE EVILCOLL");
var_dump($stmt->execute() instanceof SQLite3Result);
echo "done\n";

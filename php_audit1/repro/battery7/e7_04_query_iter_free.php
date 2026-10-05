<?php
// Same idea but the statement is a query() result iterated implicitly, and the
// UDF re-assigns the holding variable + GC.
$db = new PDO('sqlite::memory:');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$db->exec("CREATE TABLE t(x)");
$db->exec("INSERT INTO t VALUES (1),(2),(3)");
$db->sqliteCreateFunction('evil', function ($v) {
    $GLOBALS['s'] = null;
    gc_collect_cycles();
    return $v;
});
$GLOBALS['s'] = $db->query("SELECT evil(x) FROM t");
foreach ($GLOBALS['s'] as $row) {
    var_dump($row);
}
echo "done\n";

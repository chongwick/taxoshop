<?php
$db = new SQLite3(':memory:');
$db->createCollation('C', function($a,$b){ global $db; $db->createCollation('C', fn($x,$y)=>strcmp($x,$y)); return strcmp($a,$b); });
$db->exec("CREATE TABLE t(x)");
$db->exec("INSERT INTO t VALUES ('b'),('a'),('c'),('d')");
$r=$db->query("SELECT x FROM t ORDER BY x COLLATE C");
while($r->fetchArray()){}
echo "E done\n";

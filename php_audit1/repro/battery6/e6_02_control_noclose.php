<?php
$db = new SQLite3(':memory:');
$db->createFunction('ok', function () { return 1; });
$stmt = $db->prepare("SELECT ok()");
var_dump($stmt->execute() instanceof SQLite3Result);
echo "done\n";

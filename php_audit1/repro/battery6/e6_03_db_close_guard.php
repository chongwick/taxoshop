<?php
$db = new SQLite3(':memory:');
$db->createFunction('evil', function () use (&$db) {
    try { $db->close(); } catch (\Throwable $e) { echo "caught: ".$e->getMessage()."\n"; }
    return 1;
});
$stmt = $db->prepare("SELECT evil()");
var_dump($stmt->execute() instanceof SQLite3Result);
echo "done\n";

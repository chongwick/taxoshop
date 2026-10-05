<?php
$db = new SQLite3(':memory:');
$db->createFunction('evil', function () {
    global $res;
    if ($res instanceof SQLite3Result) { $res->finalize(); }
    return 1;
});
$stmt = $db->prepare("SELECT evil() UNION ALL SELECT evil()");
$res = $stmt->execute();      // first row buffered; finalize fires on fetch step
while ($res->fetchArray(SQLITE3_NUM)) {}
echo "done\n";

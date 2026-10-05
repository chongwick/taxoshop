<?php
// SQLite3Stmt::close() from inside a UDF callback fired by that statement's own
// sqlite3_step(). Finalizes the running VDBE; execute() then keeps using the
// dangling stmt pointer (sqlite3_reset at sqlite3.c:1907). Not covered by the
// GH-23650 in_callback guard (that only blocks SQLite3::close).
$db = new SQLite3(':memory:');
$db->createFunction('evil', function () {
    global $stmt;
    $stmt->close();   // finalizes stmt_obj->stmt while sqlite3_step is running it
    return 1;
});
$stmt = $db->prepare("SELECT evil()");
$res = $stmt->execute();
var_dump($res);
echo "done\n";

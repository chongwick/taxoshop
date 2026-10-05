<?php
$db = new SQLite3(':memory:');
$db->createFunction('evil', function () { global $s; $s->clear(); return 1; });
$s = $db->prepare("SELECT evil() UNION ALL SELECT evil()");
$s->bindValue(1, 'x'); // create bound_params
$s->execute();
echo "B done\n";

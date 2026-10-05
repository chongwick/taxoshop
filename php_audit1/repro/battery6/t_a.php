<?php
$db = new SQLite3(':memory:');
$db->createFunction('evil', function () { global $s; $s->reset(); return 1; });
$s = $db->prepare("SELECT evil() UNION ALL SELECT evil()");
$s->execute();
echo "A done\n";

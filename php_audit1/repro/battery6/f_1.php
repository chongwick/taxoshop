<?php
$a = new SplFixedArray(4);
for ($i=0;$i<4;$i++) $a[$i] = $i;
$GLOBALS['a'] = $a;
foreach ($a as $i => $v) {
    if ($i === 0) { $a->setSize(100000); }  // erealloc grow -> buffer moves
    $x = $v;
}
echo "F1 done\n";

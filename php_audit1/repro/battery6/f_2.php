<?php
$a = new SplFixedArray(8);
for ($i=0;$i<8;$i++) $a[$i] = "v$i";
foreach ($a as $i => $v) {
    if ($i === 0) { $a->setSize(0); }  // frees elements
    $x = (string)$v;
}
echo "F2 done\n";

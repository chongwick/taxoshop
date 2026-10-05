<?php
$fa = new SplFixedArray(64);
for($i=0;$i<64;$i++)$fa[$i]=$i;
$seen=0;
foreach($fa as $k=>$v){ if($k===2){ $fa->setSize(2); } $seen++; }
echo "$seen done d02\n";

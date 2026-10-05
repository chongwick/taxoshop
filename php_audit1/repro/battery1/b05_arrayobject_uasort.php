<?php
$ao = new ArrayObject();
for($i=0;$i<8;$i++)$ao[]= $i;
$ao->uasort(function($x,$y) use($ao){ for($i=0;$i<500;$i++)$ao[]=$i; return $x<=>$y; });
echo count($ao),"\ndone b05\n";

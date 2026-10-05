<?php
$a=[];
for($i=0;$i<32;$i++)$a[]=$i;
$a[] = &$a;   // self reference
usort($a, function($x,$y){ global $a; if(is_array($x)){ $a=[1]; } return 0; });
echo count($a),"\ndone d01\n";

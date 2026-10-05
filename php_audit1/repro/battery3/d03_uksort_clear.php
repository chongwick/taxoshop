<?php
$a=[];
for($i=0;$i<32;$i++)$a["key_$i"]=$i;
$cnt=0;
uksort($a, function($x,$y) use(&$a,&$cnt){ if($cnt++<3){ $a=["only"=>1]; } return strcmp((string)$x,(string)$y); });
echo count($a),"\ndone d03\n";

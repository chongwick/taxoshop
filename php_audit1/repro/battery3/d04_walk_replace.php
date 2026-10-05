<?php
$a=range(1,64);
array_walk($a, function(&$v,$k) use(&$a){ if($k===1){ $a=[0=>'a',1=>'b']; } });
echo count($a),"\ndone d04\n";

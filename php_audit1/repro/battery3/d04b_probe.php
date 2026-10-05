<?php
$a=range(1,64); $n=0;
array_walk($a, function(&$v,$k) use(&$a,&$n){ if($k===1 && $n++<5){ $a=[0=>'a',1=>'b']; echo "replace $n mem=".memory_get_usage()."\n"; } });
echo "n=$n done\n";

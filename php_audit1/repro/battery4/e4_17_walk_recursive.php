<?php
$a = ['x'=>range(0,1000), 'y'=>range(0,1000), 'z'=>range(0,1000)];
$GLOBALS['a']=&$a;
$n=0;
array_walk_recursive($a, function(&$v,$k) use(&$n){ if($n++==5){ unset($GLOBALS['a']['y']); $GLOBALS['a']['x']=[1]; gc_collect_cycles(); } $v=$v; });
var_dump(count($a));
echo "OK\n";

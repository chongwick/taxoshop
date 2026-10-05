<?php
$a = range(0,3000); $GLOBALS['a']=&$a;
$r = array_reduce($a, function($c,$v){ static $n=0; if($n++==5){ $GLOBALS['a']=[]; gc_collect_cycles(); } return $c+$v; }, 0);
var_dump($r);
echo "OK\n";

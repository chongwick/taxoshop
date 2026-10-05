<?php
$a = range(0,3000); $b = range(0,3000); $GLOBALS['b']=&$b;
$r = array_map(function($x,$y){ static $n=0; if($n++==5){ $GLOBALS['b']=[]; gc_collect_cycles(); } return $x+$y; }, $a, $b);
var_dump(count($r));
echo "OK\n";

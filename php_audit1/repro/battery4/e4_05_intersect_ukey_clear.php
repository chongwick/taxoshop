<?php
$GLOBALS['b'] = array_fill_keys(range(0,2000),1);
$a = array_fill_keys(range(0,2000),1);
$k = function($x,$y){ static $n=0; if($n++==5){ $GLOBALS['b']=[]; gc_collect_cycles(); } return $x<=>$y; };
var_dump(count(array_intersect_ukey($a,$GLOBALS['b'],$k)));
echo "OK\n";

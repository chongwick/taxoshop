<?php
$GLOBALS['b'] = array_map(fn($i)=>"v$i", range(0,2000));
$a = array_map(fn($i)=>"v$i", range(0,2000));
$cmp = function($x,$y){ static $n=0; if($n++==5){ $GLOBALS['b']=[]; gc_collect_cycles(); } return strcmp((string)$x,(string)$y); };
$k = function($x,$y){ return strcmp((string)$x,(string)$y); };
var_dump(count(array_udiff_uassoc($a,$GLOBALS['b'],$cmp,$k)));
echo "OK\n";

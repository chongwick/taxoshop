<?php
$a = array_map(fn($i)=>"v$i", range(0,3000));
$GLOBALS['a'] =& $a;
$b = ['x'];
$cmp = function($x,$y){ static $n=0; if($n++==3){ $GLOBALS['a']=[]; gc_collect_cycles(); } return strcmp((string)$x,(string)$y); };
var_dump(count(array_udiff($a,$b,$cmp)));
echo "OK\n";

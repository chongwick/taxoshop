<?php
class E { function __toString(){ $GLOBALS['s'] = []; gc_collect_cycles(); return "aaa"; } }
$s = [ new E() ];
for($i=0;$i<3000;$i++) $s[] = "aaa$i";
$GLOBALS['s'] =& $s;                 // reference: reassignment frees the HT
$r = preg_replace('/a/', 'b', $s);   // frameless 3-arg
var_dump(is_array($r));
echo "OK\n";

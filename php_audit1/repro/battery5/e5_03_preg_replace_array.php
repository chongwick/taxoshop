<?php
class E { function __toString(){ $GLOBALS['rep'] = []; gc_collect_cycles(); return "b"; } }
$re = []; $rep = [];
for($i=0;$i<3000;$i++){ $re[]='/a/'; $rep[]="b$i"; }
$rep[1] = new E();                   // second replacement frees $rep
$GLOBALS['rep'] =& $rep;
$r = preg_replace($re, $rep, 'aaaa');
var_dump(is_string($r));
echo "OK\n";

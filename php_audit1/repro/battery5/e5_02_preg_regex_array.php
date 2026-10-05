<?php
class E { function __toString(){ $GLOBALS['re'] = []; gc_collect_cycles(); return "/a/"; } }
$re = [ new E() ];
for($i=0;$i<3000;$i++) $re[] = '/a/';
$GLOBALS['re'] =& $re;
$r = preg_replace($re, 'b', 'aaaa');
var_dump(is_string($r));
echo "OK\n";

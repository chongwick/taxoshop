<?php
class E { function __toString(){ $GLOBALS['s'] = []; gc_collect_cycles(); return "aaa"; } }
$s = [ new E() ];
for($i=0;$i<3000;$i++) $s[] = "aaa$i";
$GLOBALS['s'] =& $s;
$r = call_user_func('preg_replace', '/a/', 'b', $s);
var_dump(is_array($r));
echo "OK\n";

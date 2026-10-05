<?php
$a = range(0,3000);
$ref =& $a; $GLOBALS['a'] =& $a;
usort($a, function($x,$y){ static $n=0; if($n++==3){ $GLOBALS['a'][0]="poison"; } return $x<=>$y; });
var_dump(count($a));
echo "OK\n";

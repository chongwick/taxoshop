<?php
class E { function __toString(){ $GLOBALS['a'] = []; return "zzz"; } }
$a = array_map(fn($i)=>"v$i", range(0, 2000));
$a[] = "needle";
$GLOBALS['a'] =& $a;
var_dump(array_search(new E(), $a));
echo "done\n";

<?php
class E { function __toString(){ $GLOBALS['a'] = []; return "zzz"; } }
$a = array_map(fn($i)=>"v$i", range(0, 2000));
$a[] = "needle";
$GLOBALS['a'] =& $a;               // haystack is now a reference
var_dump(in_array(new E(), $a));   // object compare -> __toString frees $a mid-scan
echo "done\n";

<?php
class E { function __toString(){ $GLOBALS['a']=[]; gc_collect_cycles(); return "zzz"; } }
$a = array_map(fn($i)=>"v$i", range(0,3000)); $a[]= "match";
$GLOBALS['a']=&$a;
var_dump(in_array(new E(), $a));
echo "OK\n";

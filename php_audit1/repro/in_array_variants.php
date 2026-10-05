<?php
function mk(){ $a = array_map(fn($i)=>"v$i", range(0,2000)); $a[]="needle"; return $a; }
class E { function __toString(){ $GLOBALS['a']=[]; return "zzz"; } }

echo "A: frameless 2-arg\n";
$a = mk(); $GLOBALS['a']=&$a;
var_dump(@in_array(new E(), $a));

echo "B: 3-arg (frameless_3?)\n";
$a = mk(); $GLOBALS['a']=&$a;
var_dump(@in_array(new E(), $a, false));

echo "C: call_user_func (no frameless)\n";
$a = mk(); $GLOBALS['a']=&$a;
var_dump(@call_user_func('in_array', new E(), $a));
echo "END\n";

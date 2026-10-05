<?php
function mk(){ $a=array_map(fn($i)=>"v$i",range(0,2000)); $a[]="needle"; return $a; }
class E { function __toString(){ $GLOBALS['a']=[]; return "zzz"; } }
$which = $argv[1] ?? '';
$a = mk(); $GLOBALS['a']=&$a;
switch($which){
 case 'in2':  var_dump(in_array(new E(),$a)); break;
 case 'in3':  var_dump(in_array(new E(),$a,false)); break;
 case 'search': var_dump(array_search(new E(),$a)); break;   // no frameless -> framed
 case 'cuf':  var_dump(call_user_func('in_array',new E(),$a)); break; // framed
 case 'keys': var_dump(count(array_keys($a, new E()))); break; // array_keys w/ search_value
}
echo "END $which\n";

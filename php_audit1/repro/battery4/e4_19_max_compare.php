<?php
class E { public $i; function __construct($i){$this->i=$i;} function __toString(){ static $n=0; if($n++==4){ $GLOBALS['a']=[]; gc_collect_cycles(); } return sprintf("%05d",$this->i); } }
$a=[]; for($i=0;$i<3000;$i++)$a[]=new E($i);
$GLOBALS['a']=&$a;
var_dump((string)max($a));
echo "OK\n";

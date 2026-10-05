<?php
class E { public $i; function __construct($i){$this->i=$i;} function __toString(){ static $n=0; if($n++==4){ $GLOBALS['a']=[]; gc_collect_cycles(); } return "v".$this->i; } }
$a=[]; for($i=0;$i<2000;$i++)$a[]=new E($i);
$GLOBALS['a']=&$a;
$b=[new E(999999)];
var_dump(count(array_udiff($a,$b,fn($x,$y)=>strcmp((string)$x,(string)$y))));
echo "OK\n";

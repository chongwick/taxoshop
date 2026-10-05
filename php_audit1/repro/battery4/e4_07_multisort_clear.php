<?php
class E { public $i; function __construct($i){$this->i=$i;} function __toString(){ static $n=0; if($n++==4){ $GLOBALS['col2']=[]; gc_collect_cycles(); } return sprintf("%05d",$this->i%7); } }
$col1=[]; for($i=0;$i<2000;$i++)$col1[]=new E($i);
$col2=range(0,1999); $GLOBALS['col2']=&$col2;
array_multisort($col1, SORT_STRING, $col2);
var_dump(count($col2));
echo "OK\n";

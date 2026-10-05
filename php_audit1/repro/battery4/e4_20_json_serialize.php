<?php
class E implements JsonSerializable { public $i; function __construct($i){$this->i=$i;} function jsonSerialize():mixed{ static $n=0; if($n++==4){ $GLOBALS['a']=[]; gc_collect_cycles(); } return $this->i; } }
$a=[]; for($i=0;$i<3000;$i++)$a[]=new E($i);
$GLOBALS['a']=&$a;
echo strlen(json_encode($a)),"\n";
echo "OK\n";

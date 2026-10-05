<?php
class E { public $fa; public $i; function __construct($fa,$i){$this->fa=$fa;$this->i=$i;} function __toString(){ static $n=0; if($n++==2){ $this->fa->setSize(2); gc_collect_cycles(); } return "v".$this->i; } }
$fa = new SplFixedArray(2000);
for($i=0;$i<2000;$i++)$fa[$i]=null;
for($i=0;$i<2000;$i++)$fa[$i]=new E($fa,$i);
$s=''; foreach($fa as $v){ $s.=(string)$v; }
var_dump(strlen($s));
echo "OK\n";

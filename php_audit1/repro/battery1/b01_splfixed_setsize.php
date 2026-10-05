<?php
$fa = new SplFixedArray(8);
class E { public $fa; function __toString(){ $this->fa->setSize(1); return "x"; } }
for($i=0;$i<8;$i++){ $e=new E; $e->fa=$fa; $fa[$i]=$e; }
foreach($fa as $v){ echo (string)$v; }
echo "\ndone b01\n";

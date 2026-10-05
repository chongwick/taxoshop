<?php
$l = new SplDoublyLinkedList();
class E2 { public $l; function __toString(){ for($i=0;$i<100;$i++)$this->l->push($i); return "x"; } }
for($i=0;$i<5;$i++){ $e=new E2; $e->l=$l; $l->push($e); }
foreach($l as $v){ echo is_object($v)?(string)$v:$v; }
echo "\ndone b02\n";

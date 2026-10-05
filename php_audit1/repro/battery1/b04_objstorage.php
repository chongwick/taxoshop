<?php
$s = new SplObjectStorage();
class E4 { public $s; function __toString(){ for($i=0;$i<100;$i++)$this->s->attach(new stdClass); return "x"; } }
for($i=0;$i<5;$i++){ $e=new E4; $e->s=$s; $s->attach($e, $e); }
foreach($s as $o){ echo (string)$s->getInfo(); }
echo "\ndone b04\n";

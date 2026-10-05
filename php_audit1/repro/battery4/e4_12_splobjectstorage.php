<?php
$s = new SplObjectStorage();
$objs=[]; for($i=0;$i<2000;$i++){ $o=new stdClass; $objs[]=$o; $s->attach($o,$i); }
$n=0;
foreach($s as $o){ if($n++==5){ foreach($objs as $o2)$s->detach($o2); gc_collect_cycles(); } $x=$s->getInfo(); }
var_dump($s->count());
echo "OK\n";

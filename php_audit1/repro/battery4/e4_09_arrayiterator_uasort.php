<?php
$it = new ArrayIterator(range(0,2000));
$it->uasort(function($x,$y) use($it){ static $n=0; if($n++==3){ for($k=0;$k<50;$k++)$it[]="x$k"; } return $x<=>$y; });
var_dump($it->count());
echo "OK\n";

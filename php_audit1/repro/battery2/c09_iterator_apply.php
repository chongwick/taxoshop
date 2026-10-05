<?php
$ai = new ArrayIterator([1,2,3,4,5]);
iterator_apply($ai, function() use($ai){ static $n=0; if($n++<3){ $ai->append(99); } return true; }, []);
echo count($ai),"\ndone c09\n";

<?php
class S { public $n; function __construct($n){$this->n=$n;}
  function __toString(){ global $a; array_splice($a, 0, 4); return sprintf('%09d',$this->n); } }
$a=[];
for($i=0;$i<16;$i++)$a[]=new S($i);
sort($a, SORT_STRING);
echo count($a),"\ndone d05\n";

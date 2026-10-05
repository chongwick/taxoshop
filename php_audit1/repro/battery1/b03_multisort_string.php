<?php
class E3 { public $n; function __construct($n){$this->n=$n;} function __toString(){ global $b; for($i=0;$i<2000;$i++)$b[]=$i; return (string)$this->n;} }
$a=[]; for($i=0;$i<8;$i++)$a[]=new E3(8-$i);
$b=[]; for($i=0;$i<8;$i++)$b[]=$i;
array_multisort($a, SORT_STRING, $b);
echo count($a)," ",count($b),"\ndone b03\n";

<?php
$a=[3,1,2]; $b=[1,2,3];
$refs=[]; $refs[]=&$a; $refs[]=&$b;
array_multisort($a, $b);
// reentrancy via object in one array with SORT_STRING + reference aliasing
class R{ public $n; function __construct($n){$this->n=$n;} function __toString(){ global $z; $z[0]=array_fill(0,5000,'y'); return (string)$this->n; } }
$z=[[new R(3),new R(1),new R(2)], [1,2,3]];
array_multisort($z[0], SORT_STRING, $z[1]);
echo count($z[0]),"\ndone c05\n";

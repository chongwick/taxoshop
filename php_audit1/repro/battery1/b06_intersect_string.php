<?php
class E6 { public $n; function __construct($n){$this->n=$n;} function __toString(){ global $x; for($i=0;$i<2000;$i++)$x[]="v$i"; return (string)$this->n; } }
$x=[]; for($i=0;$i<8;$i++)$x[]=new E6($i);
$y=[]; for($i=0;$i<8;$i++)$y[]="$i";
print_r(array_intersect($x,$y));
echo "done b06\n";

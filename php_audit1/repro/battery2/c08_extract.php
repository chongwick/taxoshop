<?php $a=['x'=>1,'y'=>2]; extract($a, EXTR_REFS); $b=compact('x','y','nonexistent'); print_r($b); echo "ok\n";

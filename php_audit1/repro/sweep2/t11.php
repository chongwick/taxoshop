<?php $a=range(1,10); @array_splice($a, PHP_INT_MIN, PHP_INT_MAX, [0]); echo "ok\n";

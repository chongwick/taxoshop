<?php
$M=PHP_INT_MAX; $m=PHP_INT_MIN;
@intdiv($m,-1); @($m % -1); @($m * -1); @(-$m); @abs($m);
@($M+1); @($M*2); @(1<<70); @($m<<2); @gmp_pow?0:0;
echo "u02 ok\n";

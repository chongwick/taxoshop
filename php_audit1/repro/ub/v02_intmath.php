<?php
function t($lbl,$fn){ try{ $v=$fn(); }catch(\Throwable $e){} echo "$lbl\n"; }
$M=PHP_INT_MAX; $m=PHP_INT_MIN;
t('intdiv', fn()=>intdiv($m,-1));
t('mod', fn()=>$m % -1);
t('abs_min', fn()=>abs($m));
t('gmp_abs', fn()=>extension_loaded('gmp')?gmp_abs($m):0);
t('shift', fn()=>$m << 1);
t('base_convert', fn()=>base_convert("ffffffffffffffff",16,2));
t('bindec', fn()=>bindec(str_repeat("1",128)));
t('dechex_min', fn()=>dechex($m));
echo "v02 done\n";

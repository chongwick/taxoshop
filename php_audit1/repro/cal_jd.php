<?php
$vals = [PHP_INT_MAX, PHP_INT_MIN, PHP_INT_MAX-1, 2147483647, 2147483648, 4294967296,
         9223372036854775807, -9223372036854775807, 1000000000000, 536838867000];
foreach($vals as $v){
  foreach(['jdtojewish','jdtofrench','jdtojulian','jdtogregorian'] as $fn){
    try { $r=@$fn($v); } catch(\Throwable $e) {}
  }
}
echo "done\n";

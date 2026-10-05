<?php
foreach([1000000000, 2000000000, PHP_INT_MAX, -2000000000] as $y){
  @easter_days($y); @easter_date($y);
}
@jdtogregorian(PHP_INT_MAX); @jdtogregorian(-1); @jdtogregorian(PHP_INT_MIN);
@gregoriantojd(1, 1, PHP_INT_MAX); @gregoriantojd(13, 40, 2000000000);
@jdtojewish(PHP_INT_MAX); @jewishtojd(13, 40, 1000000000);
@jdtofrench(PHP_INT_MAX); @frenchtojd(20, 40, 100000000);
@jdtojulian(PHP_INT_MAX); @juliantojd(20, 40, PHP_INT_MAX);
@unixtojd(PHP_INT_MAX); @jdtounix(PHP_INT_MAX); @cal_from_jd(PHP_INT_MAX, CAL_JEWISH);
echo "u01 ok\n";

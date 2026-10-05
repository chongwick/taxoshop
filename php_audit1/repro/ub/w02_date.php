<?php
function t($lbl,$fn){ try{ $fn(); }catch(\Throwable $e){} echo "$lbl\n"; }
t('dc_intmin', fn()=>date_create("@-9223372036854775808"));
t('dc_intmax', fn()=>date_create("@9223372036854775807"));
t('interval_huge', function(){ $d=new DateTime("@0"); $d->add(new DateInterval("P".PHP_INT_MAX."Y")); });
t('interval_sec', function(){ $d=new DateTime("@0"); $i=new DateInterval("PT0S"); $i->s=PHP_INT_MAX; $d->add($i); });
t('diff_extremes', function(){ $a=new DateTime("@-9223372036854775807"); $b=new DateTime("@9223372036854775807"); $a->diff($b); });
t('modify_huge', function(){ $d=new DateTime("@0"); $d->modify(PHP_INT_MAX." years"); });
t('strtotime_huge', fn()=>strtotime(PHP_INT_MAX." years"));
t('gmdate_huge', fn()=>gmdate("r", PHP_INT_MAX));
t('mktime', fn()=>mktime(0,0,0,PHP_INT_MAX,PHP_INT_MAX,PHP_INT_MAX));
t('settime', function(){ $d=new DateTime("@0"); $d->setDate(PHP_INT_MAX,PHP_INT_MAX,PHP_INT_MAX); $d->format("r"); });
echo "w02 done\n";

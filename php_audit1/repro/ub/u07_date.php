<?php
@gmdate("Y", PHP_INT_MAX); @gmdate("Y", PHP_INT_MIN);
@date_create("@".PHP_INT_MAX); @date_create("@".PHP_INT_MIN);
try{ $d=new DateTime("@0"); $d->add(new DateInterval("P999999999Y")); }catch(\Throwable $e){}
@mktime(0,0,0,1,1,PHP_INT_MAX); @strtotime("Jan 1 ".PHP_INT_MAX);
echo "u07 ok\n";

<?php $a=[]; $a[PHP_INT_MAX]=1; @$a[]=2; var_dump(array_key_last($a));

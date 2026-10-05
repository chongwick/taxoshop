<?php if(!extension_loaded('gmp')){echo "no gmp\n";exit;} $x=gmp_import(str_repeat("\xff",64)); echo gmp_strval(gmp_export($x)!==false?$x:gmp_init(0)),"\n"; echo "ok\n";

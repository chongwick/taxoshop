<?php
if(!extension_loaded('bcmath')){echo "no bc\n";return;}
@bcpow("2", "9223372036854775807"); @bcpow("10","1000000", 1000000);
@bcscale(PHP_INT_MAX); @bcmul("1e1000","1e1000"); @bccomp("1", "2", PHP_INT_MAX);
@bcpowmod("123456789","987654321","1000", -1);
echo "u05 ok\n";

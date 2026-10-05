<?php
if(!extension_loaded('gmp')){echo "no gmp\n";return;}
@gmp_pow(2, PHP_INT_MAX); @gmp_fact(PHP_INT_MAX); @gmp_binomial(5, PHP_INT_MAX);
@gmp_pow(gmp_init(2), -1); @gmp_root(gmp_init(-8), 2); @gmp_nextprime(gmp_init(-5));
echo "u06 ok\n";

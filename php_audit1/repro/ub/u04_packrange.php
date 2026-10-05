<?php
@unpack("C".PHP_INT_MAX, "abc"); @unpack("N".PHP_INT_MAX, "abcd");
@pack("x".PHP_INT_MAX); @pack("a".PHP_INT_MAX, "y");
@range(PHP_INT_MIN, PHP_INT_MAX); @range(0, PHP_INT_MAX, PHP_INT_MAX);
@range(PHP_INT_MAX, PHP_INT_MIN, 1);
echo "u04 ok\n";

<?php
@str_repeat("a", -1); @str_pad("x", -5);
@wordwrap("aaaa", PHP_INT_MAX); @chunk_split("abcd", PHP_INT_MAX);
@sprintf("%2147483647d", 1); @sprintf("%.2147483640f", 1.5); @sprintf("%-2000000000s","x");
@number_format(1.5, 2000000000);
echo "u03 ok\n";

<?php
$f = function($c){ spl_autoload_unregister($GLOBALS['f']); };
$GLOBALS['f'] = $f;
spl_autoload_register($f);
spl_autoload_register(function($c){ /* second */ });
var_dump(class_exists('NoSuchClass_XYZ', true));
echo "AL1 done\n";

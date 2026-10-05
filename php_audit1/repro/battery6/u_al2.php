<?php
class Loader { public function __invoke($c){ spl_autoload_unregister($GLOBALS['ldr']); } }
$ldr = new Loader();
$GLOBALS['ldr'] = $ldr;
spl_autoload_register($ldr);
spl_autoload_register(function($c){});
var_dump(class_exists('NoSuchClass_ABC', true));
echo "AL2 done\n";

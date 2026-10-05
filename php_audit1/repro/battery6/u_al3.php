<?php
spl_autoload_register(function($c){
    for ($i=0;$i<64;$i++) spl_autoload_register(function($x) use ($i){});
});
spl_autoload_register(function($c){});
var_dump(class_exists('NoSuchClass_QQQ', true));
echo "AL3 done\n";

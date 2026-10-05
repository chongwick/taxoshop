<?php if(!extension_loaded('mbstring')){echo "no mb\n";exit;} var_dump(count(mb_str_split(str_repeat("héllo",100),3))); echo mb_convert_encoding("\xe4\xb8\xad","UTF-8","SJIS"),"|ok\n";

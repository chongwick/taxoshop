<?php $cm=[0,0xffff,0,0xff]; var_dump(bin2hex(mb_encode_numericentity(str_repeat("\xe4\xb8\xad",100), $cm, "UTF-8")));

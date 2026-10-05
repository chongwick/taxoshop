<?php $cm=[0x0,0x10FFFF,0,0xffffff]; var_dump(mb_decode_numericentity("&#12345;&#x1F600;&#99999999;", $cm, "UTF-8"));

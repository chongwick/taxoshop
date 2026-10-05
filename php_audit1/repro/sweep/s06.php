<?php $r=sscanf("abc-123-xy", "%[a-z]-%[0-9]-%[^\n]"); var_dump($r);

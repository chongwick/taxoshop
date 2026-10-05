<?php @mb_ereg("(a+)+$", str_repeat("a",40)."b", $m); var_dump(mb_ereg_replace("(\\w)(\\w)", "\\2\\1", "abcdef")); echo "ok\n";

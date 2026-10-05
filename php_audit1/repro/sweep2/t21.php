<?php var_dump(sprintf("%\x00100000s", "x") === str_repeat("\x00",99999)."x" ? "padnul" : "other");

<?php try { str_pad("x", PHP_INT_MAX, "abc"); } catch(\Throwable $e){ echo "caught\n"; }

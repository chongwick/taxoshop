<?php try { str_repeat("abcd", PHP_INT_MAX); } catch(\Throwable $e){ echo "caught\n"; }

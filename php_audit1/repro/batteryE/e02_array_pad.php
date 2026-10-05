<?php try { array_pad([1,2], PHP_INT_MAX, 0); } catch (\Throwable $e){ echo "caught\n"; }

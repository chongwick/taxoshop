<?php try { hash_init('sha256', HASH_HMAC, ''); } catch (\Throwable $e){ echo "caught\n"; }

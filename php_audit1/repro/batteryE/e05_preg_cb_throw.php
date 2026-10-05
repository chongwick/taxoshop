<?php try { preg_replace_callback('/\d/', function($m){ throw new Exception("x"); }, "a1b2c3d4e5"); } catch(\Throwable $e){ echo "caught\n"; }

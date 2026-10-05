<?php try { echo vsprintf('%2$s %1$s %5$s', ['a','b']); } catch(\Throwable $e){ echo "caught ".$e->getMessage()."\n"; }

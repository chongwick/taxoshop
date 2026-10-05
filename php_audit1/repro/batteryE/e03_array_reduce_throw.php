<?php try { array_reduce([1,2,3,4], function($c,$i){ if($i===3) throw new Exception("x"); return array_merge((array)$c,[$i]); }, []); } catch(\Throwable $e){ echo "caught\n"; }

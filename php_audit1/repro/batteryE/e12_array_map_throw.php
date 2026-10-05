<?php try { array_map(function($a,$b){ if($a===2) throw new Exception("x"); return $a+$b; }, [1,2,3],[4,5,6]); } catch(\Throwable $e){ echo "caught\n"; }

<?php class T{ function __toString(){ throw new Exception("x"); } }
try { http_build_query(['a'=>1,'b'=>new T,'c'=>3]); } catch(\Throwable $e){ echo "caught\n"; }

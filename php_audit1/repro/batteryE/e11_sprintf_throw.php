<?php class T2{ function __toString(){ throw new Exception("x"); } }
try { sprintf("%s-%s-%s", "a", new T2, "c"); } catch(\Throwable $e){ echo "caught\n"; }

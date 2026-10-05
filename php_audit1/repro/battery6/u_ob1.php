<?php
ob_start(function($s){ @ob_end_clean(); return strtoupper($s); });
echo "hello";
ob_end_flush();
echo "\nOB1 done\n";

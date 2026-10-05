<?php
$big = str_repeat("word ", 200);
echo strlen(preg_replace_callback('/\w+/', function($m){ for($i=0;$i<300;$i++){ preg_match("/x{$i}y/", "z"); } return strtoupper($m[0]); }, $big)),"\ndone d06\n";

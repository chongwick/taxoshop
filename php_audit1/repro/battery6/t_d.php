<?php
$pats = ['/a/' => function($m){ global $pats; $pats['/x'.rand().'/']=fn($m)=>''; return 'A'; }];
$GLOBALS['pats'] = &$pats;
echo preg_replace_callback_array($pats, str_repeat('a', 50))."\n";
echo "D done\n";

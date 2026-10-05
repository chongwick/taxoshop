<?php
function run(&$subject) {
    $cb = function ($m) use (&$subject) {
        for ($i = 0; $i < 512; $i++) { $subject[] = 'g' . $i; }
        return 'R';
    };
    return preg_replace_callback('/./', $cb, $subject);
}
$subject = ['aaaa', 'bbbb', 'cccc'];
$out = run($subject);
var_dump(is_array($out) ? count($out) : strlen((string)$out));
echo "done\n";

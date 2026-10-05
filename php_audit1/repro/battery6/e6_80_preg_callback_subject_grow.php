<?php
// preg_replace_callback with an ARRAY subject: php_preg_replace_func_impl (php_pcre.c:2244)
// walks subject_ht WITHOUT GC_TRY_ADDREF, unlike preg_replace_callback_array (:2454). A
// callback that grows the subject array via a by-reference alias reallocs subject_ht mid-walk.
$cb = function ($m) {
    global $subject;
    for ($i = 0; $i < 512; $i++) { $subject[] = 'grow' . $i; }
    return 'R';
};
$subject = ['aaaa', 'bbbb', 'cccc', 'dddd'];
$GLOBALS['subject'] = &$subject;   // reference alias -> array refcount stays low
$out = preg_replace_callback('/./', $cb, $subject);
var_dump(is_array($out) ? count($out) : strlen((string)$out));
echo "done\n";

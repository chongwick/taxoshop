<?php
// DOMXPath registered php:function (MODE_SET via registerPhpFunctionNS) whose callback
// re-registers the SAME ns+name. php_dom_xpath_callback_ns_update_method_handler does
// zend_hash_update(&ns->functions,...) which runs the element dtor -> zend_fcc_dtor+efree
// on the fcc that zend_call_known_fcc (xpath_callbacks.c:441) is executing.
$doc = new DOMDocument();
$doc->loadXML('<root><a/><b/><c/></root>');
$xpath = new DOMXPath($doc);
$xpath->registerNamespace('m', 'urn:m');
$GLOBALS['xpath'] = $xpath;

$reg = function () {
    $GLOBALS['xpath']->registerPhpFunctionNS('urn:m', 'fn', function () {
        // replace self mid-call -> frees the currently-executing fcc/closure
        ($GLOBALS['reg'])();
        return 'z';
    });
};
$GLOBALS['reg'] = $reg;
$reg();

$res = $xpath->evaluate('string(m:fn())');
var_dump($res);
echo "done\n";

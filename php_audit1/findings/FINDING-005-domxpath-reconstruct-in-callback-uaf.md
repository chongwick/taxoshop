# FINDING-005 — `DOMXPath::__construct()` from inside a `php:function` callback frees the running XPath context (heap-UAF)

**Status:** CONFIRMED (clean ASan `heap-use-after-free`), APPARENTLY NOVEL. Same
"free-a-native-resource-from-inside-its-own-callback" family as FINDING-004 and the recent
`ext/dom` XPath callback fixes (GH-22077 `33a49bb4d39`, `f36660d6450`, `21e2c56aa40`,
`0c913c22081`, `fcdc4fbf858`) — but a different, unguarded vector those fixes did not cover.

**Extension:** ext/dom (DOMXPath / `Dom\XPath`).
**Macro-taxo:** workflow-0137 / workflow-0080 — reentrant user code invalidates native state
still in use.
**Build:** `taxoshop/php-asan-ubsan:current`, PHP 8.6.0-dev ZTS DEBUG @ HEAD `938a3110bf3`.

## Root cause

`php_xpath_eval()` (ext/dom/xpath.c:270) borrows the object's XPath context and evaluates:

```c
xmlXPathContextPtr ctxp = intern->dom.ptr;            // :285  borrowed, not pinned
...
xmlXPathObjectPtr xpathobjp = xmlXPathEvalExpression(BAD_CAST expr, ctxp);  // :329
ctxp->node = NULL;                                    // :330  USE
```

`xmlXPathEvalExpression` drives evaluation and, for a `php:function(...)` term, calls back into
userland (xpath.c:127/150 → `php_dom_xpath_callbacks_call_php_ns` → `zend_call_function`).

`DOMXPath::__construct()` is a plain method and may be called again on a live object. Called
**from inside that callback**, `dom_xpath_construct()` (xpath.c:155) tears down the current
context that `xmlXPathEvalExpression` is still using on the stack:

```c
xmlXPathContextPtr oldctx = intern->dom.ptr;          // == ctxp above
if (oldctx != NULL) {
    php_libxml_decrement_doc_ref(...);
    xmlXPathFreeContext(oldctx);                      // :178  FREE (ctxp freed here)
    php_dom_xpath_callbacks_dtor(&intern->xpath_callbacks);
    php_dom_xpath_callbacks_ctor(&intern->xpath_callbacks);
}
```

When the callback returns, `xmlXPathEvalExpression` keeps operating on the freed context, and
`php_xpath_eval` then executes `ctxp->node = NULL` (xpath.c:330) — a write to freed memory.
Nothing pins the context or rejects re-entrant construction; there is no `in_callback`/
`in_evaluation` guard anywhere in `xpath.c`.

The recent XPath-callback fixes hardened *node-result / GC-cycle* paths (resolving the intern of
a returned foreign-document node, tracing/clearing `node_list` for the cycle collector); none
of them prevents freeing the context itself during evaluation.

## Repro — `repro/battery6/e6_10_xpath_reconstruct_in_callback.php`

```php
<?php
$doc = new DOMDocument();
$doc->loadXML('<root><a>1</a><b>2</b><c>3</c></root>');
$xpath = new DOMXPath($doc);
$xpath->registerNamespace('php', 'http://php.net/xpath');
$xpath->registerPhpFunctions();
$GLOBALS['xpath'] = $xpath;
$d2 = new DOMDocument(); $d2->loadXML('<other/>'); $GLOBALS['d2'] = $d2;

function evil($v = null) {
    $GLOBALS['xpath']->__construct($GLOBALS['d2']);   // frees the running context
    return 'z';
}

$xpath->evaluate('string(php:function("evil"))');
```

ASan (`USE_ZEND_ALLOC=0`), exit 134 — log `logs/finding-005-e6_10_xpath_reconstruct.asan.txt`:

```
ERROR: AddressSanitizer: heap-use-after-free ... WRITE of size 8
    #0 php_xpath_eval           ext/dom/xpath.c:330:13     <- ctxp->node = NULL
freed by thread T0 here:
    #1 dom_xpath_construct      ext/dom/xpath.c:178:3      <- xmlXPathFreeContext(oldctx)
    ... zend_call_function
    php_dom_xpath_callbacks_call_php_ns  ext/dom/xpath_callbacks.c:496
    dom_xpath_ext_function_php  ext/dom/xpath.c:127
    (libxml2 xmlXPathEvalExpression)
SUMMARY: AddressSanitizer: heap-use-after-free ext/dom/xpath.c:330 in php_xpath_eval
```

Applies to both `query()` and `evaluate()`, legacy `DOMXPath` and modern `Dom\XPath`
(both route through `php_xpath_eval` / `dom_xpath_construct`). XSLTProcessor shares the same
`xpath_callbacks` registry and should be checked for the analogous transform-time re-entry.

## Fix

Guard re-entrant teardown, mirroring FINDING-004 / GH-23650. Add an "evaluating" flag (or
counter) on `dom_xpath_object`, set around `xmlXPathEvalExpression` in `php_xpath_eval`, and in
`dom_xpath_construct` throw an `Error` (e.g. "Cannot re-construct DOMXPath while an evaluation is
in progress") when it is set instead of freeing `oldctx`. Alternatively, pin the context for the
duration of the evaluation so re-construction defers the free.

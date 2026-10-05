<?php
// usage: php fuzz.php <target> <seed>
[$_, $target, $seed] = $argv + [null,'mb',0];
mt_srand((int)$seed);
function rbytes($n){ $s=''; for($i=0;$i<$n;$i++) $s.=chr(mt_rand(0,255)); return $s; }
$len = mt_rand(1, 64);
$in = rbytes($len);
$encs = ["UTF-8","UTF-16","UTF-16LE","UTF-16BE","UTF-32","UTF-7","UTF7-IMAP","HZ",
  "ISO-2022-JP","ISO-2022-JP-MS","ISO-2022-JP-2004","ISO-2022-KR","EUC-JP","EUC-JP-2004",
  "SJIS","SJIS-mac","SJIS-2004","CP932","CP51932","EUC-CN","GB18030","GBK","BIG-5","EUC-TW",
  "EUC-KR","UHC","CP1251","CP1252","ISO-8859-1","ISO-8859-8","KOI8-R","ARMSCII-8",
  "CP850","CP866","MacRoman","BASE64","QPrint","7bit","8bit","HTML-ENTITIES","CP50220","CP50221"];
switch($target){
 case 'mb':
   $from=$encs[mt_rand(0,count($encs)-1)]; $to=$encs[mt_rand(0,count($encs)-1)];
   @mb_convert_encoding($in, $to, $from);
   break;
 case 'mbdetect':
   @mb_detect_encoding($in, $encs, true);
   @mb_check_encoding($in, $encs[mt_rand(0,count($encs)-1)]);
   break;
 case 'mbereg':
   $pat=substr($in,0,mt_rand(1,8));
   @mb_ereg($pat, $in, $m);
   @mb_ereg_replace($pat, "X\\1", $in);
   break;
 case 'iconv':
   $from=$encs[mt_rand(0,count($encs)-1)]; $to=$encs[mt_rand(0,count($encs)-1)];
   @iconv($from, $to."//TRANSLIT", $in);
   @iconv($from, $to."//IGNORE", $in);
   break;
 case 'iconvmime':
   @iconv_mime_decode($in, mt_rand(0,3), "UTF-8");
   break;
 case 'uu':
   @convert_uudecode($in);
   break;
 case 'qp':
   @quoted_printable_decode($in);
   @quoted_printable_encode($in);
   break;
 case 'nument':
   $cm=[]; for($i=0;$i<mt_rand(0,8);$i++)$cm[]=mt_rand(-1000,0x120000);
   @mb_decode_numericentity($in,$cm,"UTF-8");
   @mb_encode_numericentity($in,$cm,"UTF-8");
   break;
 case 'kana':
   @mb_convert_kana($in, "KVCASrRnmMhH"[mt_rand(0,10)], "SJIS");
   break;
}
echo "ok\n";

<?php
// usage: php fuzz2.php <target> <seed>   (gd obscure decoders + others)
[$_, $target, $seed] = $argv + [null,'wbmp',0];
mt_srand((int)$seed);
function rb($n){ $s=''; for($i=0;$i<$n;$i++)$s.=chr(mt_rand(0,255)); return $s; }
$tmp = "/tmp/fz_$seed";
switch($target){
 case 'wbmp':
   // WBMP: type(0) fixhdr(0) width(mbint) height(mbint) data
   $w=mt_rand(0,300); $h=mt_rand(0,300);
   $data="\x00\x00".chr($w&0x7f).chr($h&0x7f).rb(mt_rand(0,40));
   file_put_contents($tmp, $data); @imagecreatefromwbmp($tmp); @unlink($tmp);
   break;
 case 'xbm':
   $s="#define x_width ".mt_rand(-5,5000)."\n#define x_height ".mt_rand(-5,5000)."\n".
      "static char x_bits[] = {".implode(",",array_map(fn()=>"0x".dechex(mt_rand(0,255)),range(0,mt_rand(0,20))))."};";
   file_put_contents($tmp,$s); @imagecreatefromxbm($tmp); @unlink($tmp);
   break;
 case 'xpm':
   $w=mt_rand(0,50); $h=mt_rand(0,50); $nc=mt_rand(1,4);
   $s="/* XPM */\nstatic char *x[] = {\n\"$w $h $nc 1\",\n";
   for($i=0;$i<$nc;$i++)$s.="\"".chr(97+$i)." c #".dechex(mt_rand(0,0xffffff))."\",\n";
   for($i=0;$i<$h;$i++)$s.="\"".str_repeat("a",max(0,$w))."\",\n";
   $s.="};";
   file_put_contents($tmp,$s); @imagecreatefromxpm($tmp); @unlink($tmp);
   break;
 case 'gd2':
   // GD2 magic 'gd2\0' then version/chunk headers
   $data="gd2\x00".pack("nnnnCnn", mt_rand(1,2), mt_rand(0,300), mt_rand(0,300), mt_rand(1,128), mt_rand(1,2), mt_rand(0,300), mt_rand(0,300)).rb(mt_rand(0,60));
   file_put_contents($tmp,$data); @imagecreatefromgd2($tmp); @unlink($tmp);
   break;
 case 'anystr':
   @imagecreatefromstring(rb(mt_rand(4,80)));
   break;
 case 'bmp':
   $data="BM".pack("Vv v V", mt_rand(0,1000), 0,0, 54).pack("VllvvVVllVV", 40, mt_rand(-300,300), mt_rand(-300,300), 1, mt_rand(1,32),0,0,0,0,0,0).rb(mt_rand(0,60));
   file_put_contents($tmp,$data); @imagecreatefromstring($data); @unlink($tmp);
   break;
 case 'exif':
   // minimal TIFF header + fuzz
   $data="II*\x00".pack("V",8).pack("v",mt_rand(0,20)).rb(mt_rand(0,80));
   $jpeg="\xff\xd8\xff\xe1".pack("n",strlen($data)+8)."Exif\x00\x00".$data."\xff\xd9";
   file_put_contents($tmp,$jpeg); @exif_read_data($tmp); @unlink($tmp);
   break;
 case 'finfo':
   @(new finfo(FILEINFO_NONE))->buffer(rb(mt_rand(1,120)));
   break;
}
echo "ok\n";

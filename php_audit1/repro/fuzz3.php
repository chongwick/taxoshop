<?php
[$_, $target, $seed] = $argv + [null,'fmt',0];
mt_srand((int)$seed);
function rb($n){ $s=''; for($i=0;$i<$n;$i++)$s.=chr(mt_rand(0,255)); return $s; }
function rs($chars,$n){ $s=''; $L=strlen($chars); for($i=0;$i<$n;$i++)$s.=$chars[mt_rand(0,$L-1)]; return $s; }
switch($target){
 case 'fmt':
   $spec='%'.rs("+-# 0123456789.'*\$",mt_rand(0,10)).rs("bcdeEfFgGosuxX",1);
   @vsprintf($spec.$spec, [mt_rand(-1e9,1e9), rb(5), 1.5]);
   break;
 case 'sscanf':
   $fmt=rs("%dscfxeg[]^-0123456789 \$*",mt_rand(1,12));
   @sscanf(rb(20), $fmt);
   break;
 case 'pack':
   $fmt=rs("aAhHcCsSnvlLNVqQJPfdeEgGxX@",mt_rand(1,8));
   if(mt_rand(0,1)) $fmt=preg_replace_callback('/[a-zA-Z]/', fn($m)=>$m[0].mt_rand(0,2000), $fmt);
   @pack($fmt, 1,2,3,rb(4),5);
   @unpack($fmt, rb(mt_rand(1,20)));
   break;
 case 'unser':
   // structured-ish random serialized payloads
   $types=['a:%d:{i:0;i:1;}','O:8:"stdClass":%d:{s:1:"a";i:1;}','s:%d:"ab";','a:2:{i:0;R:1;i:1;r:1;}','C:11:"ArrayObject":%d:{x:i:0;;m:a:0:{}}'];
   $p=$types[mt_rand(0,count($types)-1)];
   $p=sprintf($p, mt_rand(-5,1000));
   @unserialize($p);
   @unserialize(rb(mt_rand(2,30)));
   break;
 case 'date':
   $words=['now','+','-','year','month','week','day','hour','P','T','Y','M','D','@',(string)mt_rand(-1e18,1e18),'first','last','of','ago','next','tomorrow',':',' '];
   $s=''; for($i=0;$i<mt_rand(1,8);$i++)$s.=$words[mt_rand(0,count($words)-1)];
   @strtotime($s); try{ @new DateTime($s); }catch(\Throwable $e){}
   try{ @DateInterval::createFromDateString($s); }catch(\Throwable $e){}
   break;
 case 'gdop':
   $im=@imagecreatetruecolor(mt_rand(1,32), mt_rand(1,32));
   if(!$im){echo "ok\n";return;}
   switch(mt_rand(0,6)){
    case 0: @imagecrop($im, ['x'=>mt_rand(-100,100),'y'=>mt_rand(-100,100),'width'=>mt_rand(-10,100),'height'=>mt_rand(-10,100)]); break;
    case 1: @imagescale($im, mt_rand(-5,200), mt_rand(-5,200), mt_rand(-1,4)); break;
    case 2: @imagerotate($im, mt_rand(-720,720), 0); break;
    case 3: @imageaffine($im, [mt_rand(-9,9),mt_rand(-9,9),mt_rand(-9,9),mt_rand(-9,9),mt_rand(-99,99),mt_rand(-99,99)]); break;
    case 4: $m=[]; for($i=0;$i<9;$i++)$m[]=mt_rand(-9,9); @imageconvolution($im, [array_slice($m,0,3),array_slice($m,3,3),array_slice($m,6,3)], mt_rand(-5,5), mt_rand(-5,5)); break;
    case 5: @imagefilter($im, mt_rand(0,13), mt_rand(-500,500), mt_rand(-500,500), mt_rand(-500,500), mt_rand(0,1)); break;
    case 6: @imagegammacorrect($im, mt_rand(-5,5)/1.0, mt_rand(-5,5)/1.0); break;
   }
   break;
}
echo "ok\n";

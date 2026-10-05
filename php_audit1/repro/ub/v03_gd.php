<?php
if(!extension_loaded('gd')){echo "no gd\n";return;}
function t($lbl,$fn){ try{ $fn(); }catch(\Throwable $e){} echo "$lbl\n"; }
t('scale_neg', function(){ $im=imagecreatetruecolor(4,4); @imagescale($im,-1,-1); });
t('crop_huge', function(){ $im=imagecreatetruecolor(8,8); @imagecrop($im,['x'=>PHP_INT_MAX,'y'=>0,'width'=>10,'height'=>10]); });
t('rotate', function(){ $im=imagecreatetruecolor(8,8); @imagerotate($im, 1e300, 0); });
t('affine', function(){ $im=imagecreatetruecolor(8,8); @imageaffine($im,[1e300,0,0,1e300,0,0]); });
t('gaussian', function(){ $im=imagecreatetruecolor(4,4); @imagefilter($im, IMG_FILTER_GAUSSIAN_BLUR); });
t('setinterp_ellipse', function(){ $im=imagecreatetruecolor(50,50); @imageellipse($im, 25,25, PHP_INT_MAX, PHP_INT_MAX, 0xffffff); });
echo "v03 done\n";

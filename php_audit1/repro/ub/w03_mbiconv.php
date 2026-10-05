<?php
function t($lbl,$fn){ try{ $fn(); }catch(\Throwable $e){} echo "$lbl\n"; }
if(extension_loaded('mbstring')){
 t('strimwidth', fn()=>mb_strimwidth("hello world", 0, PHP_INT_MAX, "...", "UTF-8"));
 t('strimwidth_neg', fn()=>mb_strimwidth("hello", -PHP_INT_MAX, 3));
 t('mb_substr_huge', fn()=>mb_substr("héllo wörld", PHP_INT_MIN, PHP_INT_MAX));
 t('mb_split_huge', fn()=>mb_str_split("abcdef", PHP_INT_MAX));
 t('convert_kana', fn()=>mb_convert_kana(str_repeat("ｱ",1000), "KVC"));
}
if(extension_loaded('iconv')){
 t('iconv_substr', fn()=>iconv_substr("hello world", PHP_INT_MIN, PHP_INT_MAX, "UTF-8"));
 t('iconv_strpos', fn()=>iconv_strpos("hello","l", PHP_INT_MAX, "UTF-8"));
}
echo "w03 done\n";

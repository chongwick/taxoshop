<?php
function t($lbl,$fn){ try{ $fn(); }catch(\Throwable $e){} echo "$lbl\n"; }
t('lev_huge_costs', fn()=>levenshtein("hello world","dlrow olleh", PHP_INT_MAX, PHP_INT_MAX, PHP_INT_MAX));
t('lev_big', fn()=>levenshtein(str_repeat("a",50), str_repeat("b",50), 1000000000, 1000000000, 1000000000));
t('lev_negcost', fn()=>levenshtein("abc","xyz", -PHP_INT_MAX, -PHP_INT_MAX, -PHP_INT_MAX));
t('similar', function(){ similar_text(str_repeat("ab",1000), str_repeat("ba",1000), $p); });
t('soundex', fn()=>soundex(str_repeat("x",100000)));
t('metaphone', fn()=>metaphone(str_repeat("thx",10000), PHP_INT_MAX));
echo "w01 done\n";

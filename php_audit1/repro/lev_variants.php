<?php
function t($lbl,$fn){ try{ $r=$fn(); echo "$lbl => $r\n"; }catch(\Throwable $e){ echo "$lbl => threw\n"; } }
t('default_costs_ok', fn()=>levenshtein("kitten","sitting"));       // must NOT abort
t('cost_rep_line51', fn()=>levenshtein("ab","cd", 1, PHP_INT_MAX, 1)); // rep add
t('cost_ins_line56', fn()=>levenshtein("ab","cd", PHP_INT_MAX, 1, 1)); // ins add
t('cost_del_line48', fn()=>levenshtein("abc","x", 1, 1, PHP_INT_MAX)); // del add (line48)

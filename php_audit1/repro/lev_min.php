<?php
// Minimal: two 2-char strings + max cost weights -> DP partial-sum overflow
var_dump(levenshtein("aa", "bb", PHP_INT_MAX, PHP_INT_MAX, PHP_INT_MAX));

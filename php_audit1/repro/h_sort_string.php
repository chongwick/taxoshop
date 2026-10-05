<?php
class Evil {
    public $n;
    function __construct($n){ $this->n = $n; }
    function __toString() {
        global $a;
        // Grow the array being sorted -> force arData realloc under zend_sort
        for ($i=0; $i<2000; $i++) { $a[] = "x$i"; }
        return (string)$this->n;
    }
}
$a = [];
for ($i=0;$i<8;$i++) $a[] = new Evil($i);
sort($a, SORT_STRING);
var_dump(count($a));
echo "done\n";

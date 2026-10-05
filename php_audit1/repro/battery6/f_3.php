<?php
$a = new SplFixedArray(4);
for ($i=0;$i<4;$i++) $a[$i] = $i;
$it = $a->getIterator();
$it->rewind();
$a->setSize(100000);   // realloc while iterator active
while ($it->valid()) { $v = $it->current(); $it->next(); }
echo "F3 done\n";

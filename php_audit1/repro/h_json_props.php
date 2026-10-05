<?php
class Inner implements JsonSerializable {
    public $outer;
    function jsonSerialize(): mixed {
        // Force realloc of $outer's dynamic-property table mid-foreach
        for ($i=0;$i<128;$i++) { $k="new$i"; $this->outer->$k = $i; }
        return 1;
    }
}
$outer = new stdClass();
$inner = new Inner();
$inner->outer = $outer;
$outer->a = $inner;            // first dynamic prop -> non-optimized path
for ($i=0;$i<4;$i++){ $k="p$i"; $outer->$k = $i; }
echo json_encode($outer), "\n";
echo "done\n";

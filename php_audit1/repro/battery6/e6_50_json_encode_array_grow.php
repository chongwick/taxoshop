<?php
// json_encode array walk: php_json_encode_array (json_encoder.c:244 ZEND_HASH_FOREACH
// over myht) does NOT hold a ref on the array (only GC_TRY_PROTECT_RECURSION), unlike
// the object path (:584). A JsonSerializable element whose jsonSerialize() grows the
// SAME array via a by-reference alias reallocs myht mid-walk -> UAF. This is the
// json_encode sibling of the just-fixed serialize() bug (cc8abaf9f10 / GH-22714).
class G implements JsonSerializable {
    public $ref;
    public function jsonSerialize(): mixed {
        for ($i = 0; $i < 256; $i++) {
            $this->ref[] = 'x' . $i;   // grows $inner (the array being walked)
        }
        return ['d' => 1];
    }
}
$g = new G();
$inner = [$g, 'tail'];
$g->ref = &$inner;      // alias the array being walked
$top = [&$inner];
var_dump(strlen(json_encode($top)));
echo "done\n";

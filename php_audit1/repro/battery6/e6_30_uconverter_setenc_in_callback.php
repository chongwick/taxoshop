<?php
// UConverter fromUCallback (fires on an unconvertible char during ucnv_fromUChars)
// calls $this->setDestinationEncoding() -> php_converter_set_encoding ucnv_close()
// frees objval->dest == dest_cnv that php_converter_do_convert (converter.cpp:670)
// is actively using -> UAF inside ICU. No in_callback guard in ext/intl converter.
class Evil extends UConverter {
    public function fromUCallback($reason, $source, $codePoint, &$error): mixed {
        // reinitialize the destination converter mid-conversion
        $this->setDestinationEncoding('ascii');
        return '?';
    }
}
// dest = ascii, src = utf-8
$c = new Evil('ascii', 'utf-8');
// non-ASCII input -> unconvertible in ASCII dest -> fromUCallback fires
$out = $c->convert("A\u{00e9}B\u{00e9}C\u{00e9}D");
var_dump($out);
echo "done\n";

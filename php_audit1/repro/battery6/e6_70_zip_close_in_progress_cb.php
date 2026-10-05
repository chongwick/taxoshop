<?php
// ZipArchive progress callback fires during zip_close() (php_zip.c:650). obj->archive
// and archive->za are still live (nulled only after zip_close returns, :687). A reentrant
// $zip->close() from inside the progress callback calls zip_close(intern) again on the
// same struct zip * mid-close. No "close in progress" guard in ext/zip.
$tmp = tempnam(sys_get_temp_dir(), 'zc');
$zip = new ZipArchive();
$zip->open($tmp, ZipArchive::CREATE | ZipArchive::OVERWRITE);
for ($i = 0; $i < 64; $i++) {
    $zip->addFromString("f$i.txt", str_repeat('x', 2000));
}
$GLOBALS['zip'] = $zip;
$zip->registerProgressCallback(0.0, function ($r) {
    static $done = false;
    if (!$done) { $done = true; $GLOBALS['zip']->close(); }  // reentrant close mid-close
});
var_dump($zip->close());
echo "done\n";
@unlink($tmp);

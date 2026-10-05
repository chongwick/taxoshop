# FINDING-008 — Reentrant `ZipArchive::close()` from inside a progress/cancel callback → double `zip_close` (UAF / SEGV)

**Status:** CONFIRMED (SEGV under ASan), APPARENTLY NOVEL. Same
"free-a-native-resource-from-inside-its-own-callback" family as FINDING-004 (sqlite3) and the
merged GH-23650; a new built extension (ext/zip).

**Extension:** ext/zip (ZipArchive), requires libzip with `HAVE_PROGRESS_CALLBACK` /
`HAVE_CANCEL_CALLBACK` (libzip ≥ 1.3 / 1.6).
**Macro-taxo:** workflow-0137 / workflow-0080 — reentrant user code invalidates native state
still in use.
**Build:** `taxoshop/php-asan-ubsan:current`, PHP 8.6.0-dev ZTS DEBUG @ HEAD `938a3110bf3`,
system `libzip.so.4`.

## Root cause

`php_zipobj_close()` (ext/zip/php_zip.c:642) commits the archive:

```c
php_zip_archive *archive = obj->archive;
struct zip *intern = archive ? archive->za : NULL;
if (intern) {
    int err = zip_close(intern);        // :650  fires the progress callback; may zip_discard
    ...
}
...
if (archive) {
    archive->za = NULL;                 // :687  cleared only AFTER zip_close returns
    ...
    php_zip_archive_release(archive);   // :692
}
```

`zip_close()` (line 650) drives the write and invokes the registered progress callback
(`php_zip_progress_callback`, php_zip.c:3139 → `zend_call_known_fcc(&archive->progress_callback…)`)
and cancel callback into userland. At that point `obj->archive` and `archive->za` are **still
set** — they are cleared only after `zip_close` returns.

`ZipArchive::close()` is a plain method. Called **from inside the progress callback**, the
reentrant `php_zipobj_close()` reads the same `intern = archive->za` and calls `zip_close(intern)`
**again on the archive currently being closed on the stack**. libzip frees/`zip_discard`s the
`zip_t` in the inner call; the outer `zip_close` then continues operating on the freed archive →
use-after-free (SEGV in `zip_close`).

The only reentrancy state in ext/zip is `archive->bailout_callback`, which exists to propagate a
`zend_bailout`/exception out of the `zend_try` around the callback — it does **not** prevent the
callback from re-entering `close()`. There is no "close in progress" guard.

## Repro — `repro/battery6/e6_70_zip_close_in_progress_cb.php`

```php
<?php
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
$zip->close();
```

ASan (`USE_ZEND_ALLOC=0`), exit 134 — log `logs/finding-008-e6_70_zip_close_progress.asan.txt`:

```
ERROR: AddressSanitizer: SEGV ... READ
    #0 zip_close            (libzip.so.4+0xc958)
    #1 php_zipobj_close     ext/zip/php_zip.c:650:13     <- OUTER close, on freed archive
    #2 zim_ZipArchive_close ext/zip/php_zip.c:1715:2
```

(SEGV rather than a clean `heap-use-after-free` report because the crash lands in the
uninstrumented system `libzip`; it is nonetheless a genuine reentrant double-`zip_close` UAF.)

The cancel callback (`php_zip_cancel_callback`, php_zip.c:3194) fires from the same
`zip_close`/`extractTo` paths and is affected identically. `extractTo()` + progress callback +
reentrant `close()` is another entry.

## Fix

Mirror GH-23650 / FINDING-004: add an "operation in progress" flag on `php_zip_archive`, set
around the `zip_close()` / `zip_discard()` / extraction calls that can fire callbacks, and make
`ZipArchive::close()` (and other archive-mutating methods reachable from a callback) throw an
`Error` while it is set instead of calling `zip_close` again. The existing refcount
(`php_zip_archive_addref`/`release`) could alternatively be taken across the callback-bearing
`zip_close` so the reentrant path defers the teardown.

# FINDING-007 — `php_user_filter::filter()` removing its own filter (`stream_filter_remove`) → heap-UAF

**Status:** CONFIRMED (clean ASan `heap-use-after-free`), APPARENTLY NOVEL. Same
"free-a-native-resource-from-inside-its-own-callback" family as FINDING-004/005/006, in a fresh
sub-area: streams core / userland stream filters.

**Component:** `ext/standard/user_filters.c` + `main/streams/filter.c`.
**Macro-taxo:** workflow-0137 / workflow-0080 — reentrant user code invalidates native state
still in use.
**Build:** `taxoshop/php-asan-ubsan:current`, PHP 8.6.0-dev ZTS DEBUG @ HEAD `938a3110bf3`.

## Root cause

When a stream with a userland filter is read/written, `userfilter_filter()`
(ext/standard/user_filters.c:163) invokes the PHP `filter()` method:

```c
uint32_t orig_no_fclose = stream->flags & PHP_STREAM_FLAG_NO_FCLOSE;
stream->flags |= PHP_STREAM_FLAG_NO_FCLOSE;          // :186  guards the STREAM only
...
call_result = call_user_function(NULL, obj, &func_name, &retval, 4, args); // :211  USER CODE
...
if (stream_name != NULL) {
    zend_update_property_null(Z_OBJCE_P(obj), Z_OBJ_P(obj), ...);  // :241  USE obj=&thisfilter->abstract
    ...
}
```

`obj` is `&thisfilter->abstract` (captured at :173). The `PHP_STREAM_FLAG_NO_FCLOSE` flag added
around the call prevents the callback from `fclose()`-ing the stream — but nothing prevents the
callback from freeing **the filter itself**. `stream_filter_remove()` (streamsfuncs.c:1382) is a
plain function reachable from inside `filter()`:

```c
zend_list_close(Z_RES_P(zfilter));
php_stream_filter_remove(filter, 1);   // -> php_stream_filter_free(filter)  (filter.c:558/328)
```

So a `filter()` that calls `stream_filter_remove($ownFilterResource)` frees `thisfilter` (an
88-byte `php_stream_filter`) while `userfilter_filter` is on the stack. On return,
`userfilter_filter` dereferences the freed `obj` at user_filters.c:241, and the read/write filter
loop in `php_stream_fill_read_buffer` (streams.c:487) continues using the freed filter.

There is no "filter is currently executing / being removed" guard anywhere in `filter.c` or
`user_filters.c`; the only protection is the stream-level `NO_FCLOSE` flag.

## Repro — `repro/battery6/e6_40_filter_self_remove.php`

```php
<?php
$GLOBALS['fres'] = null;
class Evil extends php_user_filter {
    public function filter($in, $out, &$consumed, $closing): int {
        while ($bucket = stream_bucket_make_writeable($in)) {
            $consumed += strlen($bucket->data);
            stream_bucket_append($out, $bucket);
        }
        if ($GLOBALS['fres'] !== null) {
            $r = $GLOBALS['fres'];
            $GLOBALS['fres'] = null;      // avoid re-entry during the remove's flush
            stream_filter_remove($r);     // frees $this's underlying php_stream_filter
        }
        return PSFS_PASS_ON;
    }
}
stream_filter_register('evil', Evil::class);
$fp = fopen('php://memory', 'r+');
fwrite($fp, str_repeat('ABCD', 2000));
rewind($fp);
$GLOBALS['fres'] = stream_filter_append($fp, 'evil', STREAM_FILTER_READ);
fread($fp, 65536);
```

ASan (`USE_ZEND_ALLOC=0`), exit 134 — log `logs/finding-007-e6_40_filter_self_remove.asan.txt`:

```
ERROR: AddressSanitizer: heap-use-after-free  READ of size 8
    #0 userfilter_filter            ext/standard/user_filters.c:241:29
    #1 php_stream_fill_read_buffer   main/streams/streams.c:487
    ...
freed by thread T0 here:
    #3 php_stream_filter_free        main/streams/filter.c:328
    #4 php_stream_filter_remove      main/streams/filter.c:558
    #5 zif_stream_filter_remove      ext/standard/streamsfuncs.c:1402
    ... call_user_function
    #10 userfilter_filter            ext/standard/user_filters.c:211
```

Applies to read and write filter chains (both go through `userfilter_filter`).

## Fix

Guard the filter object the same way the stream is guarded. Options: (a) mark the filter as
"executing" for the duration of `userfilter_filter` and have `php_stream_filter_remove` /
`stream_filter_remove` defer the free (or throw) while set; or (b) take a reference on
`thisfilter` across the `call_user_function` and drop it after the post-call property reset at
:241 so a self-remove only detaches from the chain and the free happens after the callout
completes. The recent `47bebf87a04` fix hardened a different reentrancy in this same callback
(unsetting `StreamBucket::$data`); filter self-removal is the still-open sibling.

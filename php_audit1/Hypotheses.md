# php_audit1 — Hypotheses

Port of the **top-5 CPython macro-taxos** to PHP (`php-src`, branch `PHP-8.6-dev`,
`main/php_version.h` = 8.6.0-dev). 50 hypotheses, 10 per family. Each names a concrete
source site, maps it onto the taxonomy's precondition→critical-op→interference→failure
chain, explains why it is (potentially) buggy, and gives a PHP-level trigger.

Families (ranked by CPython issue count):

| Fam | CPython workflow | Pattern | PHP analogue of "user code" |
|-----|------------------|---------|-----------------------------|
| A | wf-0014 (38) | Borrowed/derived handle used after owner/backing invalidated | magic method / comparator / iterator / destructor mutates or frees the container whose `Bucket*`/`zval*`/`char*` was cached |
| B | wf-0080 (22) | Callback re-entrancy invalidates borrowed state mid-op | `__toString`, `compare`, `offsetGet`, `jsonSerialize`, hash/eq during a native fast path |
| C | wf-0137 (20) | Reentrant user code invalidates native state before later use | `__destruct`/`detach`/`close`/`__wakeup` clears a resource or buffer the op still uses |
| D | wf-0077 (11) | Concurrent contexts touch shared process-wide state w/o full sync | opcache SHM, ZTS/TSRM globals, signal handlers, persistent resources, `pcntl` fork |
| E | wf-0091 (10) | Error-path ownership loss (leak) in native operations | `emalloc`/`zend_string`/`zval` temporary not freed on a `RETURN_FALSE`/`goto`/exception exit |

**PHP reentrancy primer.** PHP is single-threaded per request, but arbitrary user
(PHP) code runs during: object comparison (`zend_compare` → `compare` handler / spaceship
on objects), `__toString`, `offsetGet`/`offsetExists`/`offsetSet` (`ArrayAccess`),
`Iterator::current/next/valid`, `jsonSerialize`, `Serializable`/`__serialize`/`__wakeup`,
`__destruct` (triggered by any refcount drop to 0), `__get`/`__set`, autoload, error/exception
handlers, `set_error_handler`, tick functions, and every `zend_call_function` callback
(`usort`, `array_walk`, `array_map`, `array_filter`, `preg_replace_callback`, `array_udiff`,
`SplHeap::compare`, etc.). Any of these is the PHP equivalent of CPython's reentrant
`__eq__`/`__index__`/`to_int`. The classic bug: a native loop caches `HashTable*`, a `Bucket*`,
a `char*` from `ZSTR_VAL`, or a numeric length, then a callout mutates/frees the array or
string, and the loop resumes on freed/reallocated storage.

**Known guard idioms (to check before claiming a bug).** (1) `usort`/`uasort`/`uksort` call
`zend_array_dup` (array.c:835) so in-place callback mutation is invisible → **hardened**.
(2) `ZEND_HASH_FOREACH` + a `SEPARATE_ARRAY`/refcount-1 assumption; if the array is
copy-on-write shared or the loop re-reads `nNumUsed` each step it may be safe.
(3) `GC_TRY_PROTECT_RECURSION` in json/var. (4) `zend_string` args hold a ref, so a borrowed
`char*` into a **parameter** string is usually safe unless the string is separated/released.
Each hypothesis notes the relevant guard to falsify.

---

## Family A — wf-0014: borrowed / derived handle used after invalidation

> Precondition: code retains a non-owning `Bucket*`, `zval*`, `char*`, `HashTable*`, or cached
> count while a callout can free/resize/replace the target. Failure: UAF / OOB / corruption.

### A1 — `array_multisort` restructure uses stale `array_size` after object comparison
- **Site:** `ext/standard/array.c` `PHP_FUNCTION(array_multisort)`, sort at `array.c:6397`,
  restructure loop `array.c:6402-6440` (`hash->arData[k] = indirect[k][i]`).
- **Pattern:** `indirect[k][i]` are borrowed `Bucket` copies pointing into the input arrays
  `hashes[i]`. `zend_sort(..., php_multisort_compare, ...)` calls `zend_compare`, which for
  **object** elements invokes the user `compare` handler / spaceship. That callback can mutate
  one of the still-live input arrays (they are not `dup`'d like `usort`), reallocating its
  `arData`. `array_size` and the `indirect` pointers were captured before the sort; the
  restructure then writes `array_size` buckets into a possibly-shrunk `hash`.
- **Why buggy:** unlike `php_usort` (which `zend_array_dup`s), multisort sorts the arrays *in
  place* by proxy through `indirect`; the borrowed bucket snapshot and `array_size` are not
  revalidated after the comparison callouts.
- **Trigger:** `array_multisort($a, $b)` where `$a` holds objects whose `__toString`/spaceship
  (`Stringable`/`class C{function __toString(){ $GLOBALS['b'][]=1; ... }}`) appends to / clears
  one of the participating arrays during comparison. Look for OOB write in restructure.

### A2 — `array_walk` passes a by-ref `zval*` into a bucket the callback can unset
- **Site:** `ext/standard/array.c` `php_array_walk` (`array.c:1389`), element fetch + callback
  at `array.c:1440-1490`; recursion at `array.c:1484`.
- **Pattern:** the walk fetches a live pointer `zv` into the array's bucket and passes it
  **by reference** to the user callback. If the callback `unset()`s that key or triggers a
  rehash/repack (e.g. adds many keys), the bucket storage moves/frees while `zv` (and the
  saved hash position) is still used for the write-back and the next iteration.
- **Why buggy:** array_walk deliberately supports mutation of the *value in place*, so it holds
  a borrowed slot across arbitrary user code; the guard is position-based re-lookup — verify
  whether it re-derives the slot after the call or reuses `zv`.
- **Trigger:** `array_walk($arr, function(&$v,$k) use (&$arr){ $arr = []; /* or unset all */ });`
  with a large `$arr` to force `arData` realloc/free; watch the post-call write-back.

### A3 — `array_udiff` / `array_uintersect` retain `Bucket*` lists across user comparator
- **Site:** `ext/standard/array.c` diff/intersect engines, `array.c:5190-5295` (intersect),
  `array.c:5794-5899` (diff); `php_array_user_compare_unstable` at `array.c:758`.
- **Pattern:** the algorithm builds `lists[i]` = arrays of `Bucket*` into each input array, then
  `zend_sort`s and linearly compares them using the **user** comparator (`zend_call_function`,
  `array.c:769/783`). The comparator can mutate any input array, freeing the buckets the
  `lists[]` still point to; subsequent compares dereference dangling `Bucket*`.
- **Why buggy:** the pointer lists are snapshotted once; inputs are not `dup`'d; the comparator
  is arbitrary user code invoked between dereferences.
- **Trigger:** `array_udiff($a, $b, fn($x,$y)=>((int)($a[]=1)) <=> 0)` — comparator appends to
  `$a`, reallocating its `arData` mid-sort/compare.

### A4 — `ArrayIterator`/`ArrayObject` borrowed position across `offsetSet` growth
- **Site:** `ext/spl/spl_array.c` — `spl_array_it_*` iterator methods and `Bucket`/position
  bookkeeping; foreach over an `ArrayObject` while its inner `HashTable` is mutated.
- **Pattern:** SPL array iterators cache a `HashPosition`/`Bucket*` into the wrapped
  `HashTable`. A user `offsetSet`/`append` during iteration (via overridden methods or a
  callback in the loop body) can rehash/repack the table, invalidating the cached position.
- **Why buggy:** SPL exposes the raw wrapped array; the iterator's derived position is a
  borrowed handle into storage the user can resize mid-loop.
- **Trigger:** subclass `ArrayObject`, iterate it, and inside the loop `$this[]=...` a few
  thousand times to force realloc; check iterator's next `current()`.

### A5 — `str_replace` with array subject caches `ZSTR_VAL` across `__toString` of search/replace
- **Site:** `ext/standard/string.c` `php_str_replace_common` / `php_char_to_str_ex`; buffer
  pointer captured from the subject `zend_string`.
- **Pattern:** when `search`/`replace` are objects/arrays, conversion (`zval_get_string` →
  `__toString`) runs user code. If a cached `char*` into a *separated* subject buffer is held
  across that conversion and the user code drops the last ref / triggers COW separation, the
  pointer dangles.
- **Why buggy:** parameter strings normally hold a ref (safe), but intermediate separated
  buffers created for in-place replacement are owned locally and may be released on the error
  branch while a derived `char*` is retained.
- **Trigger:** `str_replace([new Stringable...], 'x', $subject)` where `__toString` mutates a
  variable aliasing the subject; combined with a large subject to force separation.

### A6 — `sort`/`asort` (`zend_compare`) borrowed buckets when elements are objects
- **Site:** `ext/standard/array.c` `php_sort`/`php_asort` → `zend_hash_sort` →
  `zend_sort(..., php_array_data_compare_unstable, ...)` (`array.c` ~line 480-520).
- **Pattern:** the non-user sorts (`sort`, `asort`, `ksort`) do **not** `dup` the array (only
  the `u*` variants do, via `php_usort`). For object elements `zend_compare` calls the compare
  handler = user code, which can mutate the very array being sorted, invalidating the
  `Bucket`s that `zend_sort` swaps.
- **Why buggy:** the "user callback" is hidden inside `zend_compare` (object comparison), so the
  `dup` guard that protects `usort` does not apply to `sort` of objects.
- **Trigger:** `$a=[new C, new C, ...]; sort($a);` where `C::__toString`/compare does
  `$GLOBALS['a'][]=new C;` — array grows/reallocs while `zend_sort` holds bucket pointers.

### A7 — `in_array`/`array_search` loose match caches element pointer across `__toString`
- **Site:** `ext/standard/array.c` `php_search_array` (`array.c` ~line 1600-1700),
  `ZEND_HASH_FOREACH_*` with `fast_equal_check_function`/`zend_compare`.
- **Pattern:** loose (`==`) search compares each borrowed element `entry` against `value`;
  object comparison runs user code that can `unset`/reassign the array, freeing `entry` or
  moving `arData` while the foreach position is cached.
- **Why buggy:** `ZEND_HASH_FOREACH` walks `arData` by index; a rehash/free during the compare
  makes the cached `nNumUsed`/pointer stale.
- **Trigger:** `in_array($needle, $arr)` with `$needle`/elements being objects whose comparison
  clears `$arr`.

### A8 — `array_flip` / `array_column` borrowed key `zval` across implicit stringify
- **Site:** `ext/standard/array.c` `PHP_FUNCTION(array_column)` and `array_flip` foreach loops.
- **Pattern:** these iterate the source table and use borrowed `zval*` values as keys, calling
  string conversion for object values. A `__toString` that mutates the source array during the
  loop invalidates the foreach cursor / borrowed value pointer.
- **Why buggy:** the derived key handle and the source cursor are both borrowed across a
  user-code stringify boundary.
- **Trigger:** `array_column($rows, null, $colWithStringableThatMutatesRows)`.

### A9 — `iterator_to_array` borrowed `HashTable*` while `Iterator::key/current` mutate it
- **Site:** `ext/spl/spl_iterators.c` / `Zend/zend_interfaces.c` `spl_iterator_apply` /
  `iterator_to_array` — caches the destination `HashTable*` and re-enters user `current()`/`key()`.
- **Pattern:** the collector holds a `HashTable*` (result) and repeatedly calls user iterator
  methods; if `key()`/`current()` frees or replaces the destination (e.g. via reference games
  or by throwing during a partially-built state), the retained pointer is used afterward.
- **Why buggy:** derived container handle used across arbitrary iterator user code.
- **Trigger:** custom `Iterator` whose `current()` unsets the variable holding the growing
  result array (through a reference), then continues.

### A10 — `Closure::bind`/`call` borrowed scope `zend_class_entry*`/`this` across rebinding
- **Site:** `Zend/zend_closures.c` `zend_closure_bind`/`zend_closure_call_magic`; cached
  `func.common.scope` / `this_ptr`.
- **Pattern:** binding derives handles to the target object and its class; if executing the
  bound closure triggers destruction of the original object (last ref dropped inside the call),
  a retained `this`/scope pointer dangles.
- **Why buggy:** borrowed object/scope handle held across a call that can drop the owner's ref.
- **Trigger:** `Closure::bind($fn, $obj)->__invoke()` where the invocation unsets the only other
  reference to `$obj` and the closure keeps using `$this` afterward.

---

## Family B — wf-0080: callback re-entrancy invalidates borrowed state mid-op

> A native fast path holds unowned refs / cached sizes across a user callback that clears,
> resizes, replaces, or destroys that state. PHP callbacks: comparator, hash/eq, `__toString`,
> `jsonSerialize`, encode/serialize hooks.

### B1 — `json_encode` caches `myht` + element count across `jsonSerialize()`/`__toString`
- **Site:** `ext/json/json_encoder.c` `php_json_encode_array` (`json_encoder.c:108`),
  `myht`/`prop_ht` at `:123/:208`, count `i = zend_hash_num_elements(myht)` at `:236`, loop
  `ZEND_HASH_FOREACH_KEY_VAL_IND(myht, ...)` at `:244`.
- **Pattern:** for objects, `zend_get_properties_for` may return a table, then each value is
  encoded — invoking `JsonSerializable::jsonSerialize()` / `__toString` on nested members. That
  user code can mutate the object whose `prop_ht`/`myht` was cached, or free properties, while
  the foreach continues on the stale table/count.
- **Why buggy:** `GC_TRY_PROTECT_RECURSION` (`:97`) guards against *infinite recursion*, not
  against mutation of `myht` during encoding; the cached count `i` and cursor can go stale.
- **Trigger:** object A with a property that is object B; `B::jsonSerialize()` unsets/replaces
  A's properties (via a captured reference). `json_encode($A)`.

### B2 — `serialize` foreach over `myht` across `__sleep`/`__serialize` re-entrancy
- **Site:** `ext/standard/var.c` `php_var_serialize_intern`, loops at `var.c:161/205/378/410/596`.
- **Pattern:** serialization iterates an object's/array's `myht` (`ZEND_HASH_FOREACH_KEY_VAL`)
  and calls user hooks (`__sleep` returns names; nested `__serialize`). A nested hook can mutate
  the outer container being iterated (add/remove members), invalidating the foreach cursor.
- **Why buggy:** the borrowed `myht` cursor is held across user serialization callbacks.
- **Trigger:** nested objects where inner `__serialize()` mutates the outer object's property
  table; `serialize($outer)`.

### B3 — `SplHeap`/`SplPriorityQueue` insert/extract with `compare()` mutating the heap
- **Site:** `ext/spl/spl_heap.c` `spl_ptr_heap_cmp_cb_helper` (`spl_heap.c:118`), heap array
  `heap->elements` / `spl_ptr_heap_insert`/`spl_ptr_heap_delete_top`.
- **Pattern:** sift-up/down calls the user `compare($a,$b)` (`:121`) between element swaps while
  holding raw pointers into the `heap->elements` buffer and a cached `count`. A `compare()`
  that `insert()`s/`extract()`s on the same heap can `erealloc` the buffer, dangling the sift
  pointers.
- **Why buggy:** classic CPython heapq pattern; PHP's `compare` is *fully* user-defined and
  re-entrant on the same heap object. Verify whether it re-fetches `heap->elements`/`count`
  after the callout (CPython hardened this; PHP may not).
- **Trigger:** subclass `SplHeap`; in `compare()` call `$this->insert(...)` enough to realloc.

### B4 — `array_map` caches per-array `HashPosition`/count across the user callback
- **Site:** `ext/standard/array.c` `PHP_FUNCTION(array_map)` (`array.c:7013`), multi-array path
  advancing each input's position and calling `zend_call_function`.
- **Pattern:** with N input arrays, `array_map` caches each array's cursor and `n = num
  elements`; the callback can mutate an input array (append/clear), invalidating cursors/count.
- **Why buggy:** inputs are not `dup`'d; callback is arbitrary user code; the multi-array loop
  reuses cached positions.
- **Trigger:** `array_map(function($x) use (&$b){ $b[]=1; return $x; }, $a, $b)` with `$b`
  chosen to realloc mid-map.

### B5 — `array_filter(..., ARRAY_FILTER_USE_BOTH)` borrowed value+key across callback
- **Site:** `ext/standard/array.c` `PHP_FUNCTION(array_filter)` (`array.c:6799`), foreach with
  `zend_call_function` per element.
- **Pattern:** filter iterates the source `HashTable` and passes borrowed value (and key) to the
  callback; the callback can `unset` the current/other keys or grow the array, invalidating the
  foreach cursor / borrowed `zval*`.
- **Why buggy:** the array is iterated live (COW may or may not separate it); the callback runs
  between fetch and the add-to-result.
- **Trigger:** `array_filter($a, function($v) use(&$a){ $a[]=$v; return true; }, ARRAY_FILTER_USE_BOTH);`

### B6 — `usort` comparator that swaps the array's backing (COW / dup boundary)
- **Site:** `ext/standard/array.c` `php_usort` (`array.c:815`) — `zend_array_dup` at `:835`,
  then `zend_array_sort(arr, ...)`.
- **Pattern:** the dup guard protects the *original* array, but the comparator receives borrowed
  `zval*` args (`args[0]/args[1]`, `array.c:766-768`) into the **dup'd** `arr`; a comparator
  that forces `arr` itself to be destroyed (it isn't user-reachable) is safe — but a comparator
  that throws leaves `arr` half-sorted and the write-back at `:838-841` still runs.
- **Why buggy (likely HARDENED — negative hypothesis):** dup makes this the *guarded sibling*.
  Worth confirming the exception path (`EG(exception)` after sort) doesn't leak `arr` or write a
  stale `array`. Mirrors Ruby `sort!` #20427 being fixed.
- **Trigger:** `usort($a, fn($x,$y)=>throw new Exception)`; inspect for leak/stale write, not UAF.

### B7 — `preg_replace_callback` result string used while callback mutated the match array
- **Site:** `ext/pcre/php_pcre.c` `php_pcre_replace_func_impl` (`php_pcre.c:1857`), match value
  build `populate_match_value_str` (`:942` → `ZVAL_STRINGL_FAST(val, subject+start_offset,...)`),
  callback dispatch and `result` assembly (`:1731-1824`).
- **Pattern:** each match builds a `$matches` array (borrowing `subject + offset` slices) and
  calls the user callback; the callback receives those match strings. Cached `subject`
  (`char*`, `:1168`) is derived from `subject_str` which holds a ref (safe), but the `offsets`
  array and cached `start_offset`/`last_end_offset` are reused across the callback — if the
  callback triggers a `pcre2_match_data` reuse / cache eviction (`pcre_cache_entry`), the
  offsets/`pce` may be invalidated.
- **Why buggy:** the compiled-pattern cache entry `pce` and its `match_data` are process/request
  globals; a callback that calls `preg_*` with many distinct patterns can evict/realloc the
  cache entry the outer replace still uses.
- **Trigger:** `preg_replace_callback('/./', function($m){ for(...) preg_match("/x$i/",''); return ''; }, $big)` to churn the pattern cache during replacement.

### B8 — `array_unique` (SORT_STRING) borrowed buckets across `__toString`
- **Site:** `ext/standard/array.c` `PHP_FUNCTION(array_unique)` — builds an index, sorts, then
  compares adjacent elements; object→string conversion runs user code.
- **Pattern:** the `bucketindex`/`arTmp` array (`array.c:5021`) holds `Bucket*` snapshots; the
  string comparison of object elements calls `__toString`, which can mutate the source array,
  dangling the snapshot pointers.
- **Why buggy:** snapshot taken once, compares run user code between dereferences (same shape as
  A3 but via implicit stringify rather than an explicit comparator).
- **Trigger:** `array_unique([new S, new S, ...])` where `S::__toString` appends to the array.

### B9 — `http_build_query` / `var_export` foreach across `__toString` mutation
- **Site:** `ext/standard/http.c` `php_url_encode_hash_ex`; `ext/standard/var.c`
  `php_var_export_ex` foreach loops.
- **Pattern:** both walk a live `HashTable` and stringify values (calling `__toString` on
  objects). A `__toString` that mutates the walked array/object invalidates the cursor.
- **Why buggy:** borrowed cursor across implicit stringify; no dup.
- **Trigger:** `http_build_query($a)` where a value's `__toString` does `$a[]=...`.

### B10 — `implode`/`join` caches total length then re-reads elements across `__toString`
- **Site:** `ext/standard/string.c` `php_implode` — two-pass: first sums element string
  lengths, then copies into a preallocated `zend_string`.
- **Pattern:** pass 1 computes `len` (calling `__toString` on object elements); pass 2 copies
  using that cached `len`. If a `__toString` in pass 2 returns a *different* (longer) string
  than pass 1 — or mutates the array so pass 2 sees more/longer elements — the destination
  buffer overflows.
- **Why buggy:** the classic "size computed with one callout, written with another" TOCTOU;
  `__toString` is not guaranteed pure/stable across the two passes.
- **Trigger:** array of a Stringable whose `__toString` returns a short string on the first call
  and a long one on the second (stateful counter); `implode(',', $a)` → heap overflow write.

---

## Family C — wf-0137: reentrant user code invalidates native state before later use

> Op captures native state, then a conversion/callback (`__destruct`, `detach`, `close`,
> `__wakeup`, `offsetGet`, numeric conversion) clears/frees it; op resumes on the stale view.

### C1 — Stream ops use cached `php_stream*` after a callback `fclose`s it
- **Site:** `main/streams/streams.c` `_php_stream_read`/`write`/`seek`; `ext/standard/file.c`
  wrappers holding `stream` across user filter callbacks.
- **Pattern:** a user stream filter (`php_user_filter`, `stream_filter_append`) runs PHP code
  during read/write. If the filter `fclose($fp)` (via a captured handle) or detaches the
  wrapped stream, the outer op continues using the freed `php_stream*`. Direct analogue of
  CPython #143008/#143375 (flush/seek callback detaches wrapped resource).
- **Why buggy:** the stream pointer is captured before the filter callback; no revalidation.
- **Trigger:** register a userspace filter whose `filter()` closes the same stream, then
  `fread($fp, ...)`.

### C2 — `SplFileObject`/`SplTempFileObject` cached resource across `__destruct`
- **Site:** `ext/spl/spl_directory.c` `spl_filesystem_object` — `intern->u.file.stream` reused
  across method calls that can trigger destruction.
- **Pattern:** a method fetches `intern->u.file.stream`, then invokes user code (e.g.
  `getCsvControl`/iteration calling overridden methods) that unsets the only ref to the object,
  running `__destruct` → `fclose`, freeing the stream the outer method still uses.
- **Why buggy:** borrowed stream handle across a user-code boundary that can finalize the owner.
- **Trigger:** subclass `SplFileObject`, in an overridden iterator method drop `$this`'s last
  external reference; continue file read.

### C3 — `mysqli`/`PDO` statement uses cached handle after `close()` in a fetch callback
- **Site:** `ext/mysqli/mysqli_api.c` / `ext/pdo/pdo_stmt.c` fetch loops with
  `PDO::FETCH_FUNC`/`FETCH_CLASS` (constructor is user code).
- **Pattern:** `fetchAll(PDO::FETCH_FUNC, $cb)` or `FETCH_CLASS` runs the callback/constructor
  per row while the native fetch holds the statement/result handle; the callback can `closeCursor()`
  or free the statement, invalidating the handle used for the next row.
- **Why buggy:** result/statement handle borrowed across per-row user code. Analogue of CPython
  sqlite #143198/#143662 (factory closes connection mid-iteration).
- **Trigger:** `$stmt->fetchAll(PDO::FETCH_FUNC, function($x) use($stmt){ $stmt->closeCursor(); });`

### C4 — `unserialize` uses cached `HashTable*`/object across `__wakeup`/`offsetSet`
- **Site:** `ext/standard/var_unserializer.re` (generated `var_unserializer.c`) —
  `php_var_unserialize` object/array construction, `__wakeup` and `Serializable::unserialize`
  dispatch.
- **Pattern:** during nested unserialization the parser holds a pointer to the partially-built
  container and the input buffer position; a malicious payload can trigger `__wakeup`/
  `offsetSet`/`__unserialize` that frees or replaces the container being populated, then the
  parser writes the next element through the stale pointer.
- **Why buggy:** unserialize is *the* classic PHP reentrancy sink (many historic CVEs); the
  build-then-callback ordering keeps a borrowed container across user code.
- **Trigger:** crafted serialized string with an object whose `__wakeup` clears/reassigns a
  parent array/object still being filled (R:/r: back-references make this reachable).

### C5 — `array_walk_recursive` cached parent bucket across recursive user callback
- **Site:** `ext/standard/array.c` `php_array_walk` recursion (`array.c:1484`), which recurses
  into sub-arrays while the parent foreach position is live.
- **Pattern:** recursion holds the parent array's cursor while descending; the leaf callback can
  mutate an ancestor array, invalidating the suspended parent cursor on return.
- **Why buggy:** nested borrowed cursors across arbitrary user code at every level.
- **Trigger:** nested array; leaf callback clears the top-level array via a captured reference.

### C6 — `ob_start` user handler frees the output buffer the flush path still reads
- **Site:** `main/output.c` `php_output_handler_op` / `php_output_handler_flush` — user output
  callback (`ob_start($cb)`) runs while the runtime holds the `php_output_buffer` pointer.
- **Pattern:** the flush machinery captures `context->in`/`buffer` then calls the user handler;
  a handler that calls `ob_end_clean()`/`ob_start()` re-entrantly can free/replace the buffer
  the outer flush still copies from.
- **Why buggy:** borrowed buffer across the user output handler; re-entrant `ob_*` calls are
  reachable from within a handler.
- **Trigger:** `ob_start(function($s){ ob_end_clean(); return $s; }); echo str_repeat('x',1e6); ob_end_flush();`

### C7 — `DOMDocument`/`libxml` node used after user callback frees the document
- **Site:** `ext/dom/*` node wrappers holding `xmlNodePtr` / `dom_object` back-pointers across
  `xpath`/`registerPhpFunctions` callbacks.
- **Pattern:** `DOMXPath::registerPhpFunctions` lets XPath call PHP; that callback can unset the
  `DOMDocument`, freeing the underlying `xmlDoc`, while the XPath evaluation holds `xmlNodePtr`s.
- **Why buggy:** libxml node pointers are borrowed handles into a document whose lifetime PHP
  user code controls.
- **Trigger:** XPath expression invoking a PHP function that drops the document's last ref, then
  continues node traversal.

### C8 — `iterator`/`foreach` over object with `current()` that `__destruct`s the source
- **Site:** `Zend/zend_execute.c` `FE_FETCH`/`zend_object_iterator` dispatch; iterator holds the
  object and cached iterator state across `current()`/`next()`.
- **Pattern:** a user `Iterator::current()` that unsets the only reference to the iterated
  object triggers `__destruct`, freeing iterator state the `FE_FETCH` loop resumes with.
- **Why buggy:** borrowed iterator state across user iterator methods; PHP holds a ref to the
  iterator but nested destruction of *aggregated* state may not be covered.
- **Trigger:** `IteratorAggregate` whose inner iterator `current()` frees a member the outer
  loop still reads.

### C9 — `call_user_func_array` with by-ref params after callee frees the referenced array
- **Site:** `Zend/zend_execute_API.c` `zend_call_function` — packs `zval*` args (some by-ref)
  from a borrowed args `HashTable`; callee can free/reallocate that table.
- **Pattern:** args are gathered into a live buffer referencing the caller's array; if the
  callee mutates that array (it's passed by-ref/aliased) the arg pointers dangle for remaining
  args.
- **Why buggy:** borrowed arg storage across the call it feeds.
- **Trigger:** `call_user_func_array($fn, $args)` where `$fn` clears `$args` (aliased by-ref)
  while more by-ref params remain to be bound.

### C10 — `sprintf`/`vsprintf` cached format `char*` across `__toString` of an arg
- **Site:** `ext/standard/formatted_print.c` `php_formatted_print` — caches `format` `char*`
  (`ZSTR_VAL`) and walks it while converting each arg (object → `__toString`).
- **Pattern:** the format string pointer is derived from a parameter (holds a ref → usually
  safe), **but** the arg buffer / `smart_str` result and cached arg count are held across the
  `__toString` callout, which can free an aliased arg or grow the args array.
- **Why buggy:** the intermediate `smart_str` and the borrowed arg `zval*` are used after
  arbitrary user code from a Stringable arg.
- **Trigger:** `sprintf('%s%s', $a, $b)` where `$a->__toString()` reassigns `$b` to free its
  current buffer.

---

## Family D — wf-0077: concurrent contexts touch shared process-wide state w/o full sync

> PHP is request-isolated, but genuine shared state exists: opcache SHM (across worker
> processes), ZTS/TSRM globals, async signal handlers (interrupt anywhere), persistent
> resources, `pcntl` fork. "Concurrency" = signal/fork/SHM interleaving, not threads.

### D1 — opcache `restart_in_progress` / SHM state read without full synchronization
- **Site:** `ext/opcache/ZendAccelerator.c` `ZCSG(restart_in_progress)` writes at
  `ZendAccelerator.c:292/298/308`, `accel_shared_globals` at `:115`.
- **Pattern:** multiple FPM worker processes share `accel_shared_globals` in SHM. Restart flags
  and counters are read/written with `INCREMENT`/`LOCKVAL` macros (`:152-154`) that map to
  `Interlocked*` on Windows but rely on spinlocks/`SHM` locks elsewhere; a worker can observe a
  half-published restart state and use a partially-invalidated cache.
- **Why buggy:** cross-process shared state with an ordering/publication assumption; a worker
  reading `restart_in_progress==false` while another is mid-restart may serve from a cache being
  torn down.
- **Trigger (conceptual):** high-concurrency FPM under `opcache.revalidate_freq=0` with frequent
  file changes forcing restarts; race the restart flag against script execution. (Not
  ASan-observable single-process; needs TSan-style multiprocess reasoning or SHM instrumentation.)

### D2 — Interned strings table in opcache SHM mutated during a concurrent worker read
- **Site:** `ext/opcache/zend_accelerator_util_funcs.c` / `zend_shared_alloc.c` interned-string
  buffer shared across workers.
- **Pattern:** the shared interned-string table is published to SHM; a worker interning a new
  string vs another worker reading the table can race if the publication (pointer + length)
  isn't fully fenced before the entry is visible — CPython #152741 (publish-before-init) analogue.
- **Why buggy:** shared registry publication ordering across processes.
- **Trigger:** concurrent workers each triggering new interned strings under opcache; look for a
  worker reading a half-initialized entry.

### D3 — `pcntl` async signal handler mutates `PCNTL_G` queue interrupting native code
- **Site:** `ext/pcntl/pcntl.c` `PCNTL_G(head)/(tail)/(spares)` (`pcntl.c:205`),
  `pcntl_signal_dispatch` (`:189`), `async_signals` (`:206`).
- **Pattern:** with `pcntl_async_signals(true)`, the signal handler enqueues onto the
  `PCNTL_G` linked list from *interrupt context*, which can interleave with the main flow's
  dequeue in `pcntl_signal_dispatch`, both touching `head/tail/spares` without atomicity.
- **Why buggy:** signal delivery is asynchronous "concurrency"; the queue is shared mutable
  state accessed from both handler and mainline without a lock/atomic.
- **Trigger:** tight `pcntl_async_signals(true)` loop delivering `SIGUSR1` rapidly while the
  mainline processes the queue; watch for list corruption / lost or double-freed nodes.

### D4 — `zend_signal` deferred-handler state (`SIGG(active/depth/blocked)`) reentrancy
- **Site:** `Zend/zend_signal.c` `SIGG(active)`/`(depth)`/`(blocked)` (`zend_signal.c:99-101`),
  `global_orig_handlers` (`:78`).
- **Pattern:** the deferred signal mechanism reads/writes `SIGG(depth)`/`blocked` in the signal
  handler and in `zend_signal_handler_unblock`; a signal arriving during the unblock
  read-modify-write can lose or double-run a pending signal.
- **Why buggy:** handler vs mainline access to non-atomic signal bookkeeping; `volatile` alone
  doesn't provide atomicity.
- **Trigger:** deliver signals during `ZEND_SIGNAL_HANDLER` block/unblock windows (nested
  signals).

### D5 — Persistent stream/connection resource shared across requests in the same worker
- **Site:** `main/streams/streams.c` persistent stream list `EG(persistent_list)` /
  `ext/mysqli` persistent connections.
- **Pattern:** persistent resources survive across requests in a reused FPM worker. If request N
  leaves a persistent connection in a half-torn-down state (error during shutdown) and request
  N+1 reuses it, it reads inconsistent shared state — a lifecycle/publication race across the
  request boundary rather than threads.
- **Why buggy:** shared-across-request state without a complete "clean handoff" protocol on
  error paths.
- **Trigger:** interrupt a request mid-transaction (timeout) so cleanup is partial, then reuse
  the persistent handle next request.

### D6 — ZTS/TSRM globals resized while another thread holds a `*_G()` pointer
- **Site:** `TSRM/TSRM.c` `ts_resource_ex` / `tsrm_resource_type` table growth;
  `ZEND_TSRMLS_CACHE` in ZTS builds.
- **Pattern:** in ZTS (thread-safe SAPIs) `ts_resource` grows the per-thread storage vector; a
  thread caching a `module_G()` pointer across a point where another thread registers a new
  resource type (reallocating the vector) may dangle.
- **Why buggy:** classic borrowed-pointer-across-realloc, but in the genuinely concurrent ZTS
  vector — matches wf-0077 "publication/registry" races.
- **Trigger:** ZTS build; register modules/resource types from multiple threads at startup while
  others resolve globals. (Requires ZTS + TSan build.)

### D7 — Opcache SHM `zend_accel_hash` script cache lookup vs restart clear
- **Site:** `ext/opcache/ZendAccelerator.c` `zend_accel_hash_find`/`persistent_compile_file`
  vs `accel_restart_enter`/`zend_accel_hash_clean`.
- **Pattern:** a worker looking up a compiled script in the shared hash can race a restart that
  clears/frees the hash entries (SHM), returning a pointer into freed shared memory.
- **Why buggy:** cross-process read of a shared cache during its teardown — CPython
  finalization-vs-active-context (#140257) analogue.
- **Trigger:** force `opcache_reset()` from one worker while others compile/execute cached files.

### D8 — `getenv`/`putenv` mutate shared `environ` observed by another thread (ZTS)
- **Site:** `ext/standard/basic_functions.c` `PHP_FUNCTION(putenv)`/`getenv`; libc `environ`.
- **Pattern:** `putenv` mutates the process-global `environ` array; in ZTS, another thread's
  `getenv`/`localeconv`/`tzset` reads it concurrently. Direct analogue of CPython #127081
  (thread-unsafe libc process-global state).
- **Why buggy:** process-global mutable state without cross-thread synchronization.
- **Trigger:** ZTS build, one thread `putenv` loop, another `getenv` loop → TSan races on
  `environ` / strdup'd buffers.

### D9 — `setlocale`/`localeconv` shared libc lconv across ZTS threads
- **Site:** `ext/standard/string.c` / `main/main.c` locale handling; libc `setlocale`/`localeconv`.
- **Pattern:** `setlocale` mutates process-global locale state and the `struct lconv` that
  `localeconv`/`number_format` read; concurrent ZTS threads race exactly like CPython
  FINDING-002 (localeconv vs setlocale).
- **Why buggy:** process-global libc state; PHP does not serialize locale changes across threads.
- **Trigger:** ZTS, thread A `setlocale(LC_ALL, ...)` loop, thread B `number_format`/`localeconv`.

### D10 — MT `mt_rand` / CSPRNG global state shared without sync in ZTS
- **Site:** `ext/random/*` / `ext/standard/rand.c` — engine state in module globals `RANDOM_G`.
- **Pattern:** if any RNG state is process-global (or a shared seeded engine) rather than
  per-thread, concurrent `random_int`/`mt_rand` in ZTS race on the engine state, producing
  torn reads/duplicate outputs.
- **Why buggy:** shared mutable generator state without synchronization (value-benign race but
  a sync violation, like CPython #153852 umbrella).
- **Trigger:** ZTS, multiple threads calling `mt_rand()` concurrently; TSan on the engine buffer.

---

## Family E — wf-0091: error-path ownership loss (leak) in native operations

> An owned temporary (`emalloc`, `zend_string`, `zval`, iterator, builder) is acquired before a
> fallible step; an early `RETURN_FALSE`/`goto`/exception exit skips its release → leak.

### E1 — `http_build_query` early `goto exit` before freeing an intermediate string
- **Site:** `ext/standard/http.c` `php_url_encode_hash_ex`, `goto exit` at
  `http.c:346/352/358` after building `key`/`ekey` buffers.
- **Pattern:** the encoder allocates encoded key/value `zend_string`s, then hits a `goto exit`
  on a nested-error / deprecation path; verify every `goto exit` releases the
  `smart_str`/`zend_string` allocated in that iteration.
- **Why buggy:** multiple early exits after owned temporaries — the exact wf-0091 shape.
- **Trigger:** `http_build_query` on a structure that triggers the error branch (e.g. an object
  with a throwing `__toString` mid-iteration) and check for leaked encoded buffers under
  `USE_ZEND_ALLOC=1` + leak report / valgrind.

### E2 — `array_pad` / `array_fill` leaks preallocated result on count validation failure
- **Site:** `ext/standard/array.c` `PHP_FUNCTION(array_pad)` (`array.c:4750`).
- **Pattern:** if `array_pad` allocates the result/tmp before validating `pad_size` (or hits an
  overflow check) it may `RETURN_FALSE`/throw after the allocation without freeing.
- **Why buggy:** owned intermediate created before the fallible size check — matches CPython
  #148484 (array iterator acquired before typecode validation).
- **Trigger:** `array_pad($a, PHP_INT_MAX, 0)` or a size that trips the overflow/limit check
  after allocation.

### E3 — `array_reduce` leaks the accumulator on a callback exception
- **Site:** `ext/standard/array.c` `PHP_FUNCTION(array_reduce)` (`array.c:6727`).
- **Pattern:** the running accumulator `zval` is owned across each `zend_call_function`; if the
  callback throws mid-fold, verify the partial accumulator (and the return `retval`) is
  `zval_ptr_dtor`'d before propagating the exception.
- **Why buggy:** owned intermediate across a fallible callback → leak on the exception exit
  (CPython #140406 shape: owned result before validation/failure).
- **Trigger:** `array_reduce($a, fn($c,$i)=> $i===3 ? throw new Exception : [$c], [])` with a
  non-trivial accumulator; leak-check.

### E4 — `str_repeat` / `str_pad` leaks the allocated `zend_string` on late overflow check
- **Site:** `ext/standard/string.c` `PHP_FUNCTION(str_repeat)` / `str_pad` size math.
- **Pattern:** if the result buffer is `zend_string_alloc`'d before a length-overflow/`E_ERROR`
  path, the exit leaks it. Check ordering of `ZEND_ASSUME`/overflow guards vs allocation.
- **Why buggy:** allocation-before-validation error path.
- **Trigger:** `str_repeat('ab', PHP_INT_MAX)` to force the overflow branch after any partial
  allocation.

### E5 — `preg_replace_callback` leaks `subpats`/result on a callback exception
- **Site:** `ext/pcre/php_pcre.c` `php_pcre_replace_func_impl` (`php_pcre.c:1857`),
  `result`/`match` `zend_string` and the `$matches` `HashTable`.
- **Pattern:** each iteration builds a `$matches` array and a partial `result` string; if the
  user callback throws, verify the in-progress `result` and the match array are released before
  the function bails.
- **Why buggy:** owned intermediates (`result`, `subpats`) across the fallible callback.
- **Trigger:** `preg_replace_callback('/./', fn($m)=>throw new Exception, $big)`; leak-check.

### E6 — `json_decode` leaks partially-built container on depth/error abort
- **Site:** `ext/json/json_parser.y` (generated `json_parser.tab.c`) — object/array under
  construction when `JSON_ERROR_DEPTH`/syntax error fires.
- **Pattern:** the parser owns a partially-built `zval` array/object; on a mid-parse error it
  must free the stack of in-progress containers. Verify the error path unwinds the value stack.
- **Why buggy:** owned builder state on the parse-error exit (CPython #139988 builder-leak shape).
- **Trigger:** deeply nested JSON exceeding `depth`, or a truncated payload after a large valid
  prefix; leak-check repeated calls.

### E7 — `stream_get_contents` / `fread` leaks the growth buffer on a filter error
- **Site:** `main/streams/streams.c` `_php_stream_copy_to_mem` — `smart_str`/emalloc buffer.
- **Pattern:** the accumulation buffer is owned across reads; if a stream filter or read errors
  (or a userspace wrapper throws), the buffer must be freed before returning false.
- **Why buggy:** owned growth buffer across a fallible read/filter callback.
- **Trigger:** userspace stream wrapper whose `stream_read` throws after some bytes; leak-check.

### E8 — `array_column` leaks the interim result on a bad column type mid-iteration
- **Site:** `ext/standard/array.c` `PHP_FUNCTION(array_column)`.
- **Pattern:** it builds a result array while stringifying keys (object `__toString`); if a
  later element's key conversion throws, verify the partly-built result is destroyed.
- **Why buggy:** owned partial result across a fallible per-row conversion.
- **Trigger:** `array_column($rows, 'v', $keyCol)` where one row's key is a Stringable that
  throws on the Nth call.

### E9 — `date`/`DateTime` parsing leaks `timelib_time`/error struct on invalid input
- **Site:** `ext/date/php_date.c` + `ext/date/lib/parse_date.re` — `timelib_time*` and
  `timelib_error_container*` allocated during parse.
- **Pattern:** parsing allocates `timelib` structs before validating the result; some error
  returns may skip `timelib_time_dtor`/`timelib_error_container_dtor`.
- **Why buggy:** owned parser allocation on the invalid-input exit (CPython #139751 parser-leak
  shape — decode intermediate before rejecting).
- **Trigger:** `new DateTime('totally invalid')` / `date_parse('garbage')` in a loop; leak-check.

### E10 — `hash_init`/`hash` context leaked when algo/key validation fails after alloc
- **Site:** `ext/hash/hash.c` `PHP_FUNCTION(hash_init)` / `php_hash_do_hash` — `void *context`
  from `ops->context_size` allocated before HMAC key or option validation completes.
- **Pattern:** the algorithm context (and any HMAC key buffer) is `emalloc`'d before all
  validation; an early error return (bad flags, bad key) can skip `efree(context)`.
- **Why buggy:** owned context created before the fallible validation step (CPython #148484
  exactly: resource acquired before validation).
- **Trigger:** `hash_init('sha256', HASH_HMAC, '')` (empty HMAC key error) or an invalid option
  combo; leak-check repeated calls.

---

## How to validate (next step, not done here)

Build an ASan/UBSan + leak-enabled `php-src` (analogous to the CRuby image): `./configure
--enable-debug --enable-address-sanitizer` (or `CFLAGS='-fsanitize=address,undefined'`),
`USE_ZEND_ALLOC=0` so ASan sees the allocations (PHP's `emalloc` pools otherwise hide UAFs —
this is the PHP equivalent of CPython's `PYTHONMALLOC=malloc`). Run each trigger as a `.php`
file; grep output for `AddressSanitizer:` (heap-UAF/OOB) and run under leak detection for
Family E. Families A/B/C are single-process ASan-observable; **Family D (0077) is mostly NOT
single-process observable** — like the CPython audit it needs a ZTS+TSan build (D6/D8/D9/D10) or
multi-worker FPM/SHM reasoning (D1/D2/D5/D7), so treat D as lower-yield / harder to confirm.

**Priors from the CRuby port:** the productive families there were the reentrancy ones
(0137/0080/0014) — specifically *length/pointer captured before a reentrant conversion that
shrinks the container*. The PHP analogues most likely to pay off are **B10 (implode two-pass
size TOCTOU)**, **A1/A6 (in-place sort of objects, no dup)**, **A3/B8 (udiff/unique pointer
snapshots)**, and **C4 (unserialize)**. The `usort`-family `zend_array_dup` guard (B6) is the
PHP counterpart of Ruby's fixed `sort!` — expect it hardened.

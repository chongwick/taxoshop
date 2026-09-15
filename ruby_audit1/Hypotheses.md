# CRuby Hypotheses — Top-5 Python Macro-Taxonomies Ported to Ruby

**Method.** Took the five highest-yield families from `python3 tally_bugs.py`
(`workflow-0014` 38, `workflow-0080` 22, `workflow-0137` 20, `workflow-0077` 11,
`workflow-0091` 10) and generated 10 CRuby (checkout in `ruby/`, `master`) hypotheses each.
Every hypothesis names a concrete source site, explains why it matches the pattern's
buggy shape, and sketches a trigger. These are **candidates for the `Dockerfile.cruby`
ASan/UBSan build** — not confirmed. CRuby has several hardening idioms that must be
checked before believing a hit:

- **`str_mod_check(str, p, len)`** (string.c:1001) — re-validates a String's ptr+len after a
  callout; presence of this call usually means the site is already guarded.
- **`RARRAY_PTR_USE` / `RARRAY_PTR_IN_USE_FLAG`** (array.c:301) — pins array storage during a
  block; raw `RARRAY_CONST_PTR` captured *across* a callout is the unguarded shape.
- **`rb_str_locktmp` / `str_locktmp`** — pins a String buffer for the duration of a block.
- **`RB_GC_GUARD`**, `rb_gc_writebarrier`, and the GVL — the GVL serializes ordinary threads,
  so the 0077 family mostly moves to **Ractors**, **`ObjectSpace`/GC during-sweep callbacks**,
  and process-global tables (`ruby_global_symbols`, encoding index, method/global-cache).

Trigger primitives used below: user-defined `to_str`/`to_int`/`to_ary`/`to_path`/`hash`/`==`/
`<=>`/`coerce`/`each`, a passed **block** that mutates the receiver, `Ractor`, `ObjectSpace`,
`GC.stress = true`, and `_dump`/`marshal_dump`/`_load` hooks.

---

## Family workflow-0014 — Borrowed/derived handle used after its owner is invalidated

Pattern: a non-owning pointer/view/slot survives a resize/realloc/free/mutation and is then
dereferenced. In CRuby the canonical shape is a raw `RSTRING_PTR`/`RARRAY_CONST_PTR`/embedded
struct pointer captured before a callout that reallocs or frees the backing store.

**H14-1 — `String#unpack`/`unpack1` block invalidates the source buffer.**
`pack.c` `pack_unpack_internal` caches `s = RSTRING_PTR(str)`, `send = s+len` at pack.c:1131
then runs the user block via `UNPACK_PUSH`→`rb_yield` (pack.c:1108–1111) *inside* the decode
loop. The subsequent `UNPACK_FETCH`/`memcpy` (pack.c:1140) reads through the cached `s`.
*Why buggy:* the block can `str.replace("")`, `str.clear`, or grow `str` so the shared/heap
buffer is freed or `realloc`'d, leaving `s`/`send` dangling — no `str_mod_check` after the
yield. *Trigger:* `s = ("A"*40); s.unpack("C*"){|_| s.replace("") }` (or `s << "x"*9999`).

**H14-2 — `Array#pack` associated-pointer table (`P`/`p` directives).**
`pack.c` `associated_pointer` (pack.c:146–154) walks `RARRAY_CONST_PTR(associates)` and
compares `RSTRING_PTR(tmp) == t`. The associate strings' raw pointers are recorded at
pack.c:872–877 during packing. *Why buggy:* the pointer identity stored for `P`/`p` becomes
stale if the referenced String is later reallocated (append/`force_encoding` roundtrip) before
`unpack` of the same directive dereferences it. *Trigger:* pack a `P` pointer to a string,
mutate that string to force `realloc`, then `unpack("P<n>")`.

**H14-3 — `IO::Buffer` raw base retained across `#resize`/`#free`.**
`rb_io_buffer_get_bytes_for_reading` (io_buffer.c:1199–1213) hands out `buffer->base`; the
resize path `io_buffer.c:2100–2110` `memcpy`s into a fresh mapping and frees the old, and
`#free` sets `base=NULL` (io_buffer.c:197). *Why buggy:* any C consumer or block holding the
returned `base` across a `resize`/`free` reads freed/`munmap`'d memory. *Trigger:*
`b=IO::Buffer.new(64); b.each_byte{ b.resize(1<<20) }` — or `get_string` on a slice whose
parent is resized.

**H14-4 — `IO::Buffer` slice aliasing parent base after parent teardown.**
`io_buffer.c:1962` sets `slice->base = (char*)buffer->base + offset` and pins `source`. *Why
buggy:* if the parent's mapping is replaced by `#resize` (new allocation) while a slice keeps
the old `base`, the slice points into freed storage; the `source` pin guards GC of the object
but not the `resize`-induced `free`. *Trigger:* create slice, `parent.resize(bigger)`, then
read/write the slice.

**H14-5 — `sprintf`/`format` width/precision `*` conversion frees the value string.**
`sprintf.c` captures `t = RSTRING_PTR(val)` (sprintf.c:852) after handling `*` width/precision
args, which are read with `GETNUM`/`rb_num2long` → user `to_int`. *Why buggy:* although the
result `buf` is re-fetched by the `PUSH` macro (sprintf.c:84), a `to_int` on the `*` argument
that mutates/frees the value operand before `t` is consumed yields a stale read. *Trigger:*
`format("%*s", evil, str)` where `evil.to_int` does `str.replace("")`/`str.clear`.

**H14-6 — `Struct` member array length cached across accessor callout.**
`rb_struct_members` (struct.c:82–90) compares `RSTRUCT_LEN_RAW(s)` against
`RARRAY_LEN(members)` and returns the borrowed members array. *Why buggy:* aref/aset paths
that convert an index via `to_int` (user code) after caching the members pointer can observe a
Struct whose backing was reshaped (e.g. via `instance_variable_set` on the hidden members) —
stale length/entry access. *Trigger:* subclass with `to_int` that reopens the Struct class /
mutates members during `s[evil]`.

**H14-7 — `Enumerable#min`/`max`/`minmax` retains element across `<=>`.**
`enum.c` min/max helpers hold the current-best `VALUE` (a borrowed element of the source) in a
`memo` while invoking `rb_yield`/`id_cmp` (`enum.c:93,121,251`). *Why buggy:* the comparator
can mutate the underlying collection so the retained "best" element's container slot is
overwritten/freed before the final result is read. *Trigger:* `arr.max{|a,b| arr.clear; a<=>b }`
with elements that become unreferenced after `clear` under `GC.stress`.

**H14-8 — `Hash#each`/`rb_hash_foreach` node pointer across `yield`.**
`hash_foreach_iter` (hash.c:1369) dereferences st/ar-table entry state, and the iteration
yields user code. *Why buggy:* the `ar_table`→`st_table` conversion (rehash at hash.c:2221)
reallocates the entry array; a callback that triggers rehash (mass insert) during iteration can
leave the foreach cursor pointing at freed entry storage. The `foreach_safe`/`iter_lev`
mechanism guards deletion but a *representation change* is the interesting gap. *Trigger:*
`h.each{|k,v| 100.times{|i| h[i.to_s]=i} }` starting from a small (ar) hash to force ar→st
promotion mid-iteration.

**H14-9 — `Marshal.load` retains buffer pointer across user `_load`/`allocate`.**
`marshal.c` read path holds `arg->str`/positions into the source while dispatching user
`_load`/`marshal_load` hooks (dump/load funcalls around marshal.c:188). *Why buggy:* a user
`_load` that mutates the source IO/String (for `Marshal.load(io)` or a String buffer being
re-read) can free/resize the buffer whose offset the loader resumes from. *Trigger:* custom
class whose `self._load(s)` mutates the still-being-read source string.

**H14-10 — `ObjectSpace.each_object` / finalizer holds freed object reference.**
GC finalizer dispatch (`gc.c` finalizer run at sweep) and `ObjectSpace._id2ref` can surface a
`VALUE` whose storage is mid-free. *Why buggy:* a finalizer that resurrects or references an
object being swept, or `_id2ref` racing sweep, dereferences freed slot metadata — the classic
"stale bookkeeping reference" (cf. #96572/#101975). *Trigger:* `ObjectSpace.define_finalizer`
that calls `_id2ref` on a sibling id under `GC.stress = true`.

---

## Family workflow-0080 — Callback re-entrancy invalidates borrowed container storage

Pattern: a native fast path holds unowned refs / cached sizes / iterator state across a
user callback that clears/resizes/replaces the container.

**H80-1 — `Array#pack` count/`to_int` clears the source array mid-pack.**
`pack.c` `pack_pack` reads elements via `NEXTFROM`/`THISFROM` and captures per-item String
buffers (`ptr = RSTRING_PTR(from)`, pack.c:435/820). Counts come from directives; some numeric
conversions run user code. *Why buggy:* a `to_int`/`to_str` on an element that does
`ary.clear`/`ary.replace([])` invalidates the borrowed element list the pack loop keeps
iterating. *Trigger:* `[evil, "x"].pack("A5a5")` where `evil.to_str` shrinks the array.

**H80-2 — `Array#sort!`/`sort` comparator mutates the array (ruby_qsort on live storage).**
`rb_ary_sort_bang` sorts in place over the array's own buffer; the `<=>` block/`id_cmp` is
user code. *Why buggy:* the comparator can `push`/`replace`/`clear` the array, triggering a
`realloc` of the buffer `ruby_qsort` is actively permuting → OOB/UAF on the sort scratch
pointers. (CRuby copies to a tmp for `sort` but `sort!` historically sorted live storage.)
*Trigger:* `a=(1..1000).to_a; a.sort!{|x,y| a.replace([]); x<=>y }`.

**H80-3 — `Array#fill` with block writing past a shrunk array.**
array.c:1189 `rb_ary_store(ary, i, rb_yield(LONG2NUM(i)))` in the fill-by-block loop caches the
length bound before yielding. *Why buggy:* the block can shrink `ary` (`ary.clear`), yet the
loop keeps storing up to the original `end`, and `rb_ary_store`'s expand path reallocs while an
earlier captured `RARRAY_PTR` (if any) is stale. *Trigger:* `a=[0]*100; a.fill{|i| a.clear; i}`.

**H80-4 — `Hash#[]=` / `st_insert` where key `hash`/`eql?` clears the hash.**
Hash insertion computes the bin from `rb_hash`/`eql?` (hash.c:158 `id_hash`) then writes into
the table. *Why buggy:* a key whose `hash` or `eql?` clears/rehashes the same hash between bin
computation and store leaves the insert writing through a stale `st_table`/`ar_table` pointer
(cf. #140551). *Trigger:* `h={}; k=Evil.new; def k.hash; $h.clear; 0; end; h[k]=1`.

**H80-5 — `Array#&` / `Array#|` / `uniq` set-probe with `hash`/`eql?` reentry.**
Set operations build a temporary hash keyed by elements; probing calls user `hash`/`eql?`. *Why
buggy:* reentrant mutation of a participating array during probing invalidates the borrowed
element pointers still used by the cleanup/copy phase (cf. set-intersection #143546).
*Trigger:* `(a & b)` where an element's `eql?` does `a.clear`/`b.clear`.

**H80-6 — `String#%` (format) with a Hash arg whose `to_s`/`hash` mutates the arg.**
sprintf.c named-reference path (`%{name}`) looks up the hash and formats `rb_obj_as_string`
results while holding `buf`/format cursor. *Why buggy:* the value's `to_s` can replace the
format string or the arg hash; `buf` is refetched but format-cursor `p`/`fmt` bounds are
captured (sprintf.c:278). *Trigger:* `"%{x}" % {x: evil}` where `evil.to_s` reopens/replaces
inputs.

**H80-7 — `Enumerable#sort_by`/`group_by` key callout mutating the source.**
`enum.c` collects (key,value) tuples via `rb_yield`; `group_by` inserts into a result hash
keyed by yielded keys. *Why buggy:* a key's `hash`/`eql?` that mutates the in-progress result
hash or the source enumerator invalidates the borrowed keys/values still referenced by the
outer accumulation (cf. #143543 grouping). *Trigger:* `arr.group_by{|x| k=Key.new(x); k }`
with `Key#hash` clearing the accumulator via a captured binding.

**H80-8 — `pack` `w` (BER) / `U` using a temp buffer freed by reentrant `to_int`.**
pack.c integer directives allocate a temp `buf` and cache `cp = RSTRING_PTR(buf)`
(pack.c:903/1503). *Why buggy:* if the count/value conversion runs user code that triggers GC
compaction or frees the temp (unlikely for a fresh tmp, but the *result* `res` buffer at
pack.c:799 `cp = RSTRING_PTR(res)+start` is captured before `rb_str_buf_cat` growth). A later
directive's `to_int` forcing `res` growth reallocs `res` under the stale `cp`. *Trigger:*
mixed directive string that grows `res` between capturing `cp` and writing.

**H80-9 — `IO::Buffer#each`/`#each_byte` block resizes/frees the buffer.**
io_buffer.c region loop (`io_buffer_get_bytes_for_reading` at 1199 feeding the each loop near
1720) captures `base`/`size` then yields per element. *Why buggy:* the block can call
`buffer.free`/`buffer.resize`, freeing `base` mid-iteration (no lock in the plain each path,
unlike the `locktmp`-guarded map path at io_buffer.c:555). *Trigger:*
`b=IO::Buffer.new(16); b.each_byte{ b.free }`.

**H80-10 — `Enumerator::Lazy` / `Generator` re-entrant `next` on the same enumerator.**
`enumerator.c` fiber-backed `next`/`peek` cache the last yielded value and cursor. *Why buggy:*
a block that calls `e.next` on the *same* enumerator re-enters iterator cleanup that frees the
fiber/lookahead state the outer `next` still holds (cf. iterator re-entrancy #142732).
*Trigger:* `e=[1,2,3].each; e.each{ e.next }` / lazy chain calling `self.next`.

---

## Family workflow-0137 — Reentrant argument conversion invalidates native state

Pattern: validated/captured native state (ptr, size, resource handle) survives a conversion
(`to_int`/`to_str`/`coerce`/buffer acquisition) that detaches/closes/clears the resource.

**H137-1 — `String#[]=` / `slice!` index `to_int` clears the receiver.**
`rb_str_aset` converts the index/length via `NUM2LONG`/`to_int` after (or before) capturing the
string's ptr for the splice/`memmove`. *Why buggy:* `to_int` running `self.replace("")`/
`self.clear` frees the buffer the subsequent `rb_str_splice`/`memmove` writes into. *Trigger:*
`s="abcdef"; s[evil]="X"` where `evil.to_int` does `s.clear`.

**H137-2 — `String#unpack` offset `to_int` after buffer bound capture.**
`pack_unpack_internal` reads `offset = NUM2LONG(ofs)` (pack.c:1121) then `s = RSTRING_PTR(str)`
(pack.c:1131). If `ofs` conversion is deferred/user-driven in a caller, or a later re-derive
assumes `str` unchanged. *Why buggy:* reentrant conversion of the offset that mutates `str`
invalidates `len`/`s`. *Trigger:* `str.unpack("C*", offset: evil)` where `evil.to_int` mutates
`str` (Ruby 3.3+ keyword offset).

**H137-3 — `IO#read`/`readpartial` length `to_int` closes the IO.**
io.c read entry converts the length arg and reuses the cached `fptr` (file struct) for the
`read` syscall. *Why buggy:* a length `to_int` that calls `io.close`/`io.reopen` frees/reopens
`fptr->fd` and buffers before the read runs (cf. #143375/#143662 close-during-conversion).
*Trigger:* `io.read(evil)` where `evil.to_int` closes `io`.

**H137-4 — `IO#seek`/`IO#pos=` offset `to_int` detaches the stream.**
io.c seek converts offset then acts on `fptr`. *Why buggy:* offset conversion closing/reopening
the IO leaves seek operating on a stale/closed `fptr` (mirrors #143375 seek-after-detach).
*Trigger:* `io.seek(evil)` with `evil.to_int` → `io.close`.

**H137-5 — `String#*` / `String#ljust` count `to_int` frees the pad/source.**
Repetition/justify capture the source ptr+len, convert the count/width via `to_int`, then
`memcpy` in a loop. *Why buggy:* the conversion can replace the receiver or pad string,
dangling the captured source. *Trigger:* `("ab"*evil)` where the receiver is captured then
`evil.to_int` mutates it (harder: receiver is `self`); more likely `str.ljust(evil, pad)` with
`pad` freed by `evil.to_int`.

**H137-6 — `Array#[]=` / `Array#fill` range where `to_int` clears the array.**
array.c `rb_ary_aset`→`ary_aset_by_rb_ary_store` (array.c:2465–2644) and splice
(`rb_ary_splice`, array.c:2338–2383) capture `rptr = RARRAY_CONST_PTR(ary)` (array.c:2338/2368)
then may run index conversions. *Why buggy:* `RARRAY_CONST_PTR` captured before a `to_int` that
`ary.clear`s makes `rptr` dangle before `ary_splice` copies from it (self-insert path
`self_insert` is exactly this fragile case). *Trigger:* `a[evil,2]=a` where `evil.to_int`
shrinks `a`.

**H137-7 — `Integer#pack`-style `rb_integer_pack` buffer vs reentrant size query.**
`sprintf.c:647` / pack.c:896 call `rb_integer_pack(from, RSTRING_PTR(buf), RSTRING_LEN(buf),…)`
with a pre-sized tmp. *Why buggy:* if the numeric operand is a user `Integer` subclass whose
`coerce`/`to_int` mutates the tmp/result during size negotiation, the pack writes past a
reallocated `buf`. *Trigger:* `format("%b", evil_bignum_like)` with a coercion side effect.

**H137-8 — `Regexp#match` / `String#gsub` `p`/`len` after non-iter hash lookup.**
string.c gsub non-iter path (string.c:6347) does `repl = rb_hash_aref(hash, subseq)` then
`str_mod_check`. The *hash* default proc (`Hash.new{...}`) is user code executed by `aref`.
*Why buggy:* although `str_mod_check` guards `str`, the pattern/`match` data (`match0`,
`RMATCH_BEG`) captured at string.c:6335 is *not* re-validated after the default proc runs.
*Trigger:* `str.gsub(/./, Hash.new{ str.replace("") })` — probe whether match-position reads
outrun the guard.

**H137-9 — `Marshal.dump` with a `_dump`/`marshal_dump` that mutates the write buffer.**
marshal.c `dump_funcall` (marshal.c:188) invokes user `_dump` while the dumper holds
`arg->str` (marshal.c:279) as the output buffer. *Why buggy:* a `_dump` that reads back / resizes
`arg->str` (e.g. via a shared reference to the output) invalidates the cached write position.
*Trigger:* object whose `_dump` calls `Marshal.dump` recursively on a shared buffer, or mutates
a leaked reference to the output string.

**H137-10 — `String#encode`/`force_encoding` transcode with reentrant `to_str` replacement.**
transcode.c/string.c encode path acquires source ptr+len and an econv handle, then may convert
options/replacement via `to_str`. *Why buggy:* a replacement-string `to_str` that mutates the
source frees the buffer the transcoder streams from. *Trigger:*
`s.encode("UTF-16", invalid: :replace, replace: evil)` where `evil.to_str` does `s.clear`.

---

## Family workflow-0077 — Concurrent contexts race on shared process-wide state

Note: the GVL serializes ordinary Ruby threads, so promising surfaces are **Ractors**,
**process-global tables**, **lazy caches**, and **GC/sweep** overlap. Build the
`tsan`-equivalent or run under ASan with `Ractor`/threads and `GC.stress`.

**H77-1 — `ruby_global_symbols` symbol table under concurrent Ractor `intern`.**
symbol.c:91 `ruby_global_symbols` is process-global; `next_id` uses atomics (symbol.c:330) and
`sym_set` is a concurrent set, but `set_id_entry`/`ids` directory growth (symbol.c:871
`rbimpl_atomic_value_load(&…ids)`) mixes atomic and plain access. *Why buggy:* concurrent
Ractors interning brand-new symbols can race the `ids` directory realloc/publish vs. readers
(cf. lazy-cache publication #152741/#140260). *Trigger:* N Ractors each `("sym#{rand}"*).to_sym`
on disjoint names under load.

**H77-2 — Encoding index/table lazy load across Ractors.**
`encoding.c` maintains a global encoding registry with lazy `require`-backed loading. *Why
buggy:* first concurrent use of a not-yet-loaded encoding from two Ractors can double-initialize
or race the registry array publish (cf. once-only init #140260). *Trigger:* two Ractors
simultaneously `"x".force_encoding("Shift_JIS").encode("EUC-JP")` for an encoding not yet
autoloaded.

**H77-3 — `require`/`$LOADED_FEATURES` (loaded_features index) concurrent update.**
load.c maintains the loaded-features array + an index hash. *Why buggy:* concurrent `require`
from threads (allowed to run during blocking `require` I/O) mutating the shared index vs.
readers of `$LOADED_FEATURES` (cf. shared-registry publication). *Trigger:* two threads
`require`-ing files that transitively require a common file.

**H77-4 — Inline/global method cache invalidation vs. concurrent `define_method`.**
vm_method.c global cache / `RCLASS` serial and cc (call cache) are read on dispatch and bumped
on redefinition. *Why buggy:* a Ractor redefining a shared (frozen-but-reopened) class, or
concurrent class-hierarchy mutation, races the version-counter read/write (cf. version-cache
#108253 / free-threaded cc races #153852). *Trigger:* Ractors calling a method while another
context redefines it (needs shareable class).

**H77-5 — `Ractor` shared object `object_id` inline-storage race.**
ractor.c:1880 comment: "if a T_OBJECT is shared and has no free capacity, we can't safely store
the object_id inline". *Why buggy:* computing/assigning `object_id` for a shared object from two
Ractors can race the shape/inline-slot write. *Trigger:* share one object to many Ractors, each
calls `.object_id` concurrently.

**H77-6 — `ractor_last_id` / ractor registry publication.**
ractor.c:524 `ractor_last_id` and the ractor list are updated at create/terminate. *Why buggy:*
a newly created Ractor may be published to the shared list before all fields are initialized,
racing enumerators / `Ractor.count` (cf. publish-before-init #152741, thread-list race
#150284/#154822). *Trigger:* tight `Ractor.new{}` create/exit loop while another thread reads
`Ractor.count`/dumps.

**H77-7 — Class variable / constant cache (`rb_const`) concurrent lazy fill.**
`variable.c` constant lookup caches resolution; autoloaded constants fill lazily. *Why buggy:*
concurrent first reference to an autoload constant from two threads/Ractors can double-run the
autoload or race the cache slot write. *Trigger:* `autoload :X, "x"`; two threads reference `X`
simultaneously.

**H77-8 — `Regexp` cache / `onig_region` shared reuse across Ractors.**
re.c caches compiled regex state and per-thread match registers; a Regexp literal is shareable.
*Why buggy:* concurrent `match?` on a shared Regexp that lazily compiles or mutates cached
`onig` state (e.g. named-group table) races (cf. shared-cache #153852). *Trigger:* share one
`/(?<a>.)/`, have Ractors `match?` concurrently before it's compiled.

**H77-9 — GC finalizer table / `finalizer_table` mutation during sweep.**
gc.c finalizer registration and run touch a shared table while the collector sweeps. *Why
buggy:* `define_finalizer`/`undefine_finalizer` from a thread during a GC that is dispatching
finalizers races the table (cf. finalization overlap #140257/#130091). *Trigger:*
`GC.stress=true`; thread loop registering/removing finalizers while allocating.

**H77-10 — `Thread`/`Fiber` scheduler shared timer/interval read.**
thread.c timer thread and `Thread#priority`/timeslice interval are process-global; scheduler
hook registration is shared. *Why buggy:* an unsynchronized read of a config interval while
another thread updates it (cf. interval read/update race #130605/#153014). *Trigger:* one thread
mutates scheduler/`Thread.pass` timing state while others read it under sanitizer.

---

## Family workflow-0091 — Error-path ownership loss (leak on exceptional exit)

Pattern: an owned intermediate (xmalloc'd buffer, temp object, builder, iterator) is acquired,
then a validation/`rb_raise`/longjmp exits before it is freed. Confirm with ASan leak checks
(note the image sets `detect_leaks=0`; re-enable or use LeakSanitizer/valgrind for this family).

**H91-1 — `Marshal.load` `BUFSIZ` read buffer leaked on parse error.**
marshal.c:2436 `arg->buf = xmalloc(BUFSIZ)` for the IO read path. *Why buggy:* if a malformed
stream triggers `rb_raise` (bad tag / truncated) before `clear_load_arg`/`free` runs, the raw
`buf` leaks — unless it's tied to a `T_DATA` with a free func. *Trigger:* `Marshal.load(io)`
with an IO source feeding a truncated/invalid dump so the loader raises mid-read.

**H91-2 — `pack.c` associates array / temp buffer on directive error.**
pack.c allocates temp buffers (`buf`) and the `associates` array (pack.c:874) during packing.
*Why buggy:* an invalid directive or a `to_str`/`to_int` raising after a temp is allocated but
before `str_associate`/cat exits without freeing intermediate xmalloc'd scratch. *Trigger:*
`[1,2].pack("C P")` with an operand that raises during conversion after scratch allocation.

**H91-3 — `String#unpack("m"/"u")` (base64/uu) decode buffer on malformed input.**
pack.c decode of `m`/`u` allocates a result String and a scratch region; malformed padding can
raise. *Why buggy:* an intermediate xmalloc/`ALLOCV` scratch not freed on the error return.
*Trigger:* `("!!!invalid").unpack("m")` variants crafted to raise after scratch allocation.

**H91-4 — `rb_str_format`/`sprintf` temp value leaked on format error.**
sprintf.c builds temporaries (`tmp` via `rb_integer_pack` path, sprintf.c:647) before a
malformed-format `rb_raise` ("malformed format string"). *Why buggy:* a temp created for a
conversion whose *later* directive is invalid leaks if the raise bypasses release. *Trigger:*
`format("%b%", big)` (trailing `%`) after a valid `%b` allocates `tmp`.

**H91-5 — JSON/`ext` parser intermediate on invalid token.**
`ext/json` (if built) / `strscan` parsers allocate builder state (arrays/hashes/token buffers)
then raise `ParserError` on bad input. *Why buggy:* builder/intermediate owned state not
finalized on the error path (cf. builder-leak #139988). *Trigger:* `JSON.parse('[1,2,')`
(truncated) repeatedly; watch RSS / LSan.

**H91-6 — `IO.foreach`/`readlines` line buffer on encoding error.**
io.c line reading grows a `rb_str_tmp`/`ALLOCV` line buffer; an `invalid byte sequence`
`rb_raise` during coderange scan can exit with the temp live. *Why buggy:* buffer allocated
before the fallible validation. *Trigger:* read a file with an invalid multibyte line under a
strict external encoding so the scan raises.

**H91-7 — `Dir.glob`/`Dir[]` fnmatch buffer on pattern error.**
dir.c glob allocates path-join scratch (`ALLOCV`/xmalloc) while expanding braces; a bad pattern
or `to_path` raising leaks the scratch. *Why buggy:* scratch acquired before pattern validation
completes. *Trigger:* `Dir[evil]` where `evil.to_path` raises after glob scratch is allocated,
or a brace pattern that errors mid-expansion.

**H91-8 — `Regexp.new` compile buffer on syntax error.**
re.c `rb_reg_initialize` allocates onig compile scratch, then `onig_new` can fail →
`rb_reg_raise` (RegexpError). *Why buggy:* partially built regex/onig region or the source
copy not freed on the compile-error path (cf. content-model alloc #140593). *Trigger:*
`Regexp.new("(?<a>")` (unbalanced) in a loop; watch LSan.

**H91-9 — `String#scan`/`gsub` `onig_region` on mid-scan raise.**
string.c scan allocates match-region state per iteration; if the block or a `to_str` on the
replacement raises, the region/temp for the current iteration leaks. *Why buggy:* region owned
before the fallible callout. *Trigger:* `str.gsub(/./){ raise }` rescued in a loop; monitor
region allocation growth.

**H91-10 — `Struct.new`/`Data.define` member setup leaked on invalid member.**
struct.c `struct_set_members` builds the hidden members + back-hash arrays (struct.c:108–142)
before validating member names. *Why buggy:* an invalid member (non-symbol, duplicate) raising
`rb_raise` after the back-hash array is allocated leaks that intermediate. *Trigger:*
`Struct.new(:a, :a)` / `Struct.new(:a, 123)` in a loop; watch for accumulation.

---

## Suggested verification order (highest expected yield first)

1. **H80-2 (`sort!` comparator realloc)**, **H14-1 (`unpack` block)**, **H137-6 (`Array#[]=`
   self-insert)** — classic CRuby UAF shapes with cheap triggers; run first on ASan.
2. **H14-3/H14-4/H80-9 (`IO::Buffer` resize/free)** — newer, less-swept surface; ASan-visible.
3. **H137-1/H137-3/H137-4 (index/length `to_int` closes/clears receiver)** — check whether a
   `str_mod_check`/`rb_io_check_closed` guard already exists before believing a hit.
4. **0091 family** — needs LeakSanitizer/valgrind (image runs `detect_leaks=0`); lower priority.
5. **0077 family** — needs Ractor/threads + a TSan-equivalent build; H77-1/H77-5/H77-6 (symbol
   table, shared object_id, ractor publication) are the sharpest.

**Guards to check before filing any hit:** `str_mod_check` (string.c:1001),
`RARRAY_PTR_IN_USE_FLAG` (array.c:301), `rb_str_locktmp` (io_buffer.c:555), `rb_io_check_closed`,
frozen checks, and the `iter_lev`/`foreach_safe` hash-iteration guard.

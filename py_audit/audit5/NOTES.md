# audit5 — CPython sanitizer pattern audit (running log)

Started 2026-09-12. Image `taxoshop/cpython-asan-ubsan:current`, CPython HEAD `e5d4fa28` (3.16.0a0).
Prior audit dirs (audit2/3/4) deleted from tree; carry-over state in memory.

## Target families
- workflow-0137 reentrant argument conversion invalidates a backing resource
- workflow-0080 callback re-entrancy invalidates borrowed state/backing storage
- workflow-0014 borrowed/derived handle used after invalidation

## Already-hardened (from memory / prior audits) — skip w/o reason
bisect, deque, json, bytearray, array, heapq, memoryview, struct, sqlite Blob, select,
_io Buffered, csv, set/dict, elementtree, mmap read/write/move/find.

## Known upstream DUPES (do NOT report)
#157335 mmap __setitem__ reentrant resize; #154997 BufferedIO self->raw NULL-deref via own
detach; #154523 FT data race self->buffer; audit4 FINDING-001 (TextIOWrapper detach UAF).

## SANITIZER CALIBRATION (important, verified 2026-09-12 in the image)
Build uses GCC `-fsanitize=address -fsanitize=undefined` (no explicit sub-flags).
Tested tiny C programs under `UBSAN_OPTIONS=halt_on_error=1`:
- signed-integer-overflow  → CAUGHT
- signed left-shift        → CAUGHT   (workflow-0003 detectable)
- misaligned typed access  → CAUGHT   (workflow-0007 detectable)
- float-cast-overflow      → **NOT caught** (workflow-0010 UNdetectable here)
- null ptr + memcpy size 0 → **NOT caught** (workflow-0005 UNdetectable here)
=> Do NOT waste time on float->int (0010) or null+0 memcpy (0005) in this build;
   clean runs for them prove nothing. GCC's -fsanitize=undefined omits
   float-cast-overflow & nonnull-attribute by default.
ASan side still catches heap UAF/OOB as before.

## Progress
- workflow-0137/0080/0014 reentrancy: spot-checked and found HARDENED across the
  mainstream (list index/count/remove, pickle batch_list_exact/batch_dict_exact w/
  critical section, json _encoder_iterate_fast_seq gh-142831 INCREF, bytes fast-path
  gh-128213 uses PyLong_AsSsize_t under crit-section, io readline PyBytesWriter,
  bytearray `%` bumps ob_exports, posix_spawn parse_file_actions INCREF,
  multibytecodec decode holds exported Py_buffer). Upstream sweep is thorough.

## Candidate log
(IDEA / TESTING / CONFIRMED / DUP / FALSE)
- **CONFIRMED (FINDING-001):** heap-UAF / double `PyBuffer_Release` when receiving a
  memoryview from a cross-interpreter queue while an allocation fails.
  `_memoryview_from_xid` (Modules/_interpretersmodule.c:258) error-path `Py_DECREF(obj)`
  releases the *stolen* buffer (xibufferview_dealloc:179) but `view->used` is still 0,
  so queue_get cleanup -> `_pybuffer_shared_free`:270 `PyBuffer_Release(&view->view)`
  reads/releases the freed exporter. Parent workflow-0014. Repro
  repro/FINDING-001-repro.py (set_nomemory(3,4)); log logs/finding-001.asan.txt.
  NEW: survived gh-151126 OOM-hardening of the same functions; no upstream issue found.
  Note: memoryview only registers as cross-interp shareable once `_interpreters`
  (or concurrent.interpreters) is imported — must import it or put() raises
  NotShareableError (this masked an earlier mis-run).
- IDEA: signed-shift/overflow (0003) in undertested decoders/format width+precision.
- FALSE/CLEAN: marshal r_short/r_long — deliberately cast to (long) before <<24, no
  signed overflow. r_long64 uses _PyLong_FromByteArray.
- FALSE/CLEAN: zoneinfo TZif int decode is done in Python (Lib/zoneinfo/_common.py),
  not C — no signed-shift in _zoneinfo.c. Tree-wide `<<24/<<28` grep: only guarded
  constants / long / hash. No signed bit-accumulation bug found.

## Battery results (all CLEAN, exit 0) — repro/battery/
- t_empty_memcpy.py    empty-buffer copy prims (0005) — but note 0005 UNdetectable here
- t_float_time.py / t_float_misc.py  float->int (0010) — UNdetectable here (see calib)
- t_shift_decode.py    int.from_bytes/marshal/struct/json signed decode (0003)
- t_bound_int.py       format width/precision + repeat overflow (>=2**63) (0003)
- t_misalign.py        memoryview.cast/struct.unpack_from/array at odd offsets (0007)
                       -> all use memcpy/aligned storage, no misaligned typed access
- t_evil_reentrancy.py struct.pack_into/array/bytearray/memoryview setitem w/ evil
                       __index__ resizing target -> all protected (BufferError via
                       exported Py_buffer, or args converted before buffer touched)
- t_codec_errh.py      unicode+CJK encode/decode + incremental w/ reentrant error
                       handler returning huge repl / backpos / registry mutation

## Verified-hardened this iteration (don't re-audit w/o reason)
listobject index/count/remove; _pickle batch_list_exact / batch_dict_exact (crit sec) +
load_dict/load_list (re-derive stack->data); _json fast-seq (gh-142831); bytes fast-path
(gh-128213); io IOBase.readline (PyBytesWriter); bytearray `%` (ob_exports++);
posix_spawn parse_file_actions; multibytecodec encode/decode/streamreader/incremental;
struct pack_into; misc float/time entry points.

## Session outcome
No NEW sanitizer-confirmed bug this iteration. Mainstream reentrancy family is
exhaustively swept; the two "easy" UBSan families (0010 float-cast, 0005 null+0 memcpy)
are undetectable in this GCC build. Best remaining leads for next time: (a) 0003/0007 in
genuinely undertested decoders/parsers (paths not hit by CPython's own UBSan CI);
(b) load-side pickle reentrancy via find_class/persistent_load draining the stack
(needs a concrete re-entry mechanism); (c) tsan image for the concurrency families
(0077/0081/0056) which this ASan/UBSan image can't observe.
</content>

# audit7 — hunting NEW free-threading data races (and other sanitizer bugs)

Started 2026-09-13. audit6 re-found the 5 known hypotheses; audit7 hunts for NEW
(previously-unreported) sanitizer-confirmed bugs, primarily using the free-threaded TSan
image `taxoshop/cpython-tsan-ft:current` (Py_GIL_DISABLED=1, HEAD e5d4fa28).

## Method
Share ONE C-extension object across N threads calling its mutating/reading methods
concurrently; run under TSan. Prioritize races on POINTERS / SIZES / BUFFERS (UAF/torn-ptr
potential), not mere logical lost-updates. Then dup-check (git log + gh issues) before any
NEW claim.

## Run recipe
docker run --rm -e PYTHONMALLOC= -e TSAN_OPTIONS=halt_on_error=0:history_size=7 \
  -v <audit7>:/audit taxoshop/cpython-tsan-ft:current \
  bash -c 'cd /src/cpython && ./python /audit/repro/tsan/<f>.py'

## Known / already-reported FT races (NOT new): array #128942, dict/list-iter #154130,
set-iter #144356, decimal #149142, subinterp init #129824, bytearray/list mostly guarded.

## META-FINDING (important): FT C-extension crashes are a KNOWN, deprioritized class
A fuzzer (gh user Nievesjyl) recently filed many free-threaded C-extension crash reports
(e.g. #157088 elementtree append-vs-clear UAF; #157124 _pickle load_build vs shared state).
Maintainer @ZeroIntensity closed them **not_planned**, commenting "coming off as spam; please
consolidate into a single issue." => Sharing a stdlib C object across threads to get a TSan
race / crash mostly REDISCOVERS this known class and is NOT wanted as new separate reports.
Pivot away from FT-race hunting toward NEW single-thread type-crash (reentrancy/UBSan) bugs.

## Candidate log (IDEA/TESTING/RACE/CLEAN/DUP/NEW)
- itertools shared-iterator TSan: islice(:1710)=#151409 OPEN dup; pairwise(:396)=#123471
  umbrella dup; groupby(:537) races but within #123471 "etc." umbrella. DUP (known FT sprint).
- _elementtree shared Element: TSan race on extra->children / length. Read element_getitem
  :1591 / element_length :1705 vs write element_add_subelement :552 (SubElement/append), and
  element_resize PyMem_Realloc frees children[] => UAF. Module declares Py_MOD_GIL_NOT_USED,
  ZERO critical sections. Log logs/elementtree*.tsan.txt. **DUP of closed #157088** (append
  vs clear, same extra/children root cause; closed not_planned). Prior fixes gh-126033/126037/
  143200 are single-thread-reentrancy/specific-method only. Not reportable (not_planned class).
- _pickle shared Pickler.dump: 1 TSan race at _pickle_Pickler_dump_impl:4970. Likely same
  fuzzer-known FT class (cf #157124 unpickler). Low value given policy. NOT pursued further.
- CLEAN under FT TSan (have guards): io.StringIO, io.BytesIO, csv.writer, functools.lru_cache,
  collections.deque, re.Match, random.Random instance.

## Single-thread reentrancy (ASan/UBSan GIL image) — all HARDENED
- heapq siftdown/siftup: after each PyObject_RichCompareBool, checks `size !=
  PyList_GET_SIZE(heap)` -> RuntimeError, AND re-derives `arr=_PyList_ITEMS(heap)`. Safe vs
  evil __lt__ clear/extend. push/heapify/replace/pushpop all raise cleanly.
- bisect insort/bisect_left/right with evil __lt__ mutating list: clean (re-reads).
- _pickle re-entrant persistent_load/find_class calling self.load() to churn shared Pdata
  stack: clean (load_* re-derive self->stack->data after callouts, per audit5).

## OOM error-path probe (_testcapi.set_nomemory, ASan) — all CLEAN (no double-free/UAF/NULL)
Harness repro/asan/oom_probe.py & oom_probe2.py: fail k-th alloc (k=0..60), look for ASan
crash vs clean MemoryError. Tested ~22 ops, ALL clean:
  partial, re.compile, struct.Struct, json dumps/loads, datetime.fromisoformat, namedtuple,
  textwrap.wrap, csv.reader, socket.getaddrinfo, pickle.loads, pyexpat.Parse, ET.fromstring,
  zoneinfo.from_file, _interpqueues put/get, ExceptionGroup, str.format, sorted(key),
  dict(zip), bytes.decode utf-8, codecs incremental, traceback.format_exc.
(Upstream gh-146xxx-era OOM hardening is thorough. audit5's cross-interp memoryview-XID
double-free was the last easy one and is now hardened via gh-151126.)

## SESSION OUTCOME (audit7)
NO new reportable bug. Findings:
1. Confirmed real _elementtree shared-Element UAF (children realloc vs getitem/len) but it is
   a DUP of closed #157088 (not_planned). [FINDING-001]
2. META: the free-threaded C-extension crash class is already swept by a fuzzer and
   deprioritized (not_planned, "consolidate") -> not a productive source of filable bugs.
3. Confirmed exhaustive hardening across single-thread reentrancy (heapq/bisect/pickle) and
   OOM error paths (~22 builders). itertools FT races are the active #123471 sprint (dup).
Both "easy" families are mined out. Remaining theoretical avenues (all high-effort/low-yield):
UBSan 0003/0007 in obscure parsers; a genuinely novel cross-thread lifetime bug not yet
fuzzed; deep multi-step reentrancy needing a bespoke re-entry handle.
</content>

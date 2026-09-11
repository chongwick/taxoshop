# CPython Sanitizer Audit — Running Notes

Start: 2026-09-10
Auditor: Claude Code
Goal: Structured audit of CPython main against macro-taxonomy bug patterns
(taxos/macro_taxo). Find NEW, sanitizer-confirmed, non-duplicate issues; write
each up under its parent pattern with full sanitizer output.

## Ground rules (from task)
- Stay within documented, reproducible findings.
- Do NOT speculate or file unverified reports.
- Every reported issue must be: (a) new, (b) reproduced under the sanitizer
  build, (c) not a duplicate of an open issue, (d) attributed to a parent
  pattern, (e) accompanied by full sanitizer output.

## Environment
- Host: macOS arm64, 10 cores, Docker 24.0.2 (daemon up).
- Build path: repo Dockerfile, target `asan-ubsan` (ASan+UBSan, gcc,
  --without-pymalloc, PYTHONMALLOC=malloc).
- Source reading: local checkout ./cpython @ 8f847875d60 (main).

## Log
- [setup] Created audit/ dir. Read Dockerfile, tally_bugs.py, macro_taxo/index.json.
  163 macro patterns. Read write-ups for wf-0003 (signed left-shift UB),
  wf-0005 (zero-count memcpy through null/misaligned ptr).
- [setup] Launching Docker build `--target asan-ubsan` in background.
- [build] Compiling. CFLAGS include `-fsanitize=undefined -fsanitize=address
  -fno-strict-overflow` under gcc. CAVEAT: `-fno-strict-overflow` (wrapping signed
  arith) can suppress gcc's signed-integer-overflow/shift UBSan checks, dampening
  detectability of wf-0003 (signed left-shift) and some integer-overflow cases.
  Still active: alignment (wf-0007), null/nonnull memcpy (wf-0005), array-bounds
  (wf-0032), float-cast-overflow (wf-0010), bool/enum load, pointer-overflow.
- [plan] Two-pronged: (1) run stdlib regression suite under UBSan+ASan
  halt_on_error=0 to enumerate the full finding population; (2) targeted probes.
  Then dedupe distinct sites, cross-check open gh issues, keep only new+confirmed.
  Scripts in audit/repro/{run_suite_ubsan.sh,targeted.py,triage.py}.
- [source] _pickle.c calc_binint (wf-0003 shape): max shift 24 on 64-bit long;
  cannot overflow on this ABI. Not a live candidate here.
- [build] DONE. Image cpython-asan-ubsan. Interpreter: 3.16.0a0, GCC 13.3.0,
  ASan symbols present, CONFIG_ARGS confirms --with-address-sanitizer
  --with-undefined-behavior-sanitizer.
- [validate] Sanitizer plumbing confirmed end-to-end (symbolized, source lines):
    * UBSan: corrupt ctypes obj -> "member access within misaligned address ...
      requires 8 byte alignment" at Include/object.h:234 (via GC).
    * ASan: ctypes.string_at over-read -> heap-buffer-overflow in
      PyBytes_FromStringAndSize Objects/bytesobject.c:157.
  => "no finding" results are now trustworthy negatives.
- [probes] All 5 targeted taxonomy probes completed clean (no abort). Confirms
  main already guards the historically-fixed instances (float demotion in struct,
  extreme float timestamps, zero-count memcpy on empty containers, signed-shift
  pickle roundtrip, native handle ints). New findings must come from broader
  surface coverage -> running full regression suite under sanitizers.
- [suite] Launched detached container (docker id in audit/logs/suite.cid):
  `./python -m test -j6 --timeout=400 -w`, ASAN/UBSAN halt_on_error=0,
  log_path=/out/{asan,ubsan}.<pid> mounted to audit/logs/suite/. -w reruns
  failed tests singly. Enumerating full finding population.

## FINDING-001 (confirmed, new): HZ incremental decoder OOB read
- [hunt] Focused malformed/boundary hunt (audit/repro/hunt.py) over binascii,
  struct, float-cast, datetime-iso, memoryview.cast, json, codecs-incremental,
  array. ONE hard finding: heap-buffer-overflow in hz_decode
  (Modules/cjkcodecs/_codecs_cn.c:417) via the HZ MultibyteIncrementalDecoder.
- [root cause] `if (c=='~'){ unsigned char c2 = INBYTE2; REQUIRE_INBUF(2); ...}`
  INBYTE2 == (*inbuf)[1] dereferences the 2nd byte BEFORE REQUIRE_INBUF(2) proves
  it exists. On a lone '~' (inleft==1) -> 1-byte read past buffer end.
- [invariant audit] grep of INBYTE2/3/4 vs REQUIRE_INBUF across
  _codecs_{cn,hk,kr,jp,tw}.c: line 417 is the SOLE place where the read precedes
  the check. Sibling GB branch (same fn, 442-443) orders it correctly. Strong
  signal this is an accidental outlier, not intended.
- [why incremental] one-shot b'~'.decode('hz') does NOT trip (bytes carries an
  in-allocation trailing NUL). Incremental path pends the '~' then re-decodes
  from a tight PyMem_Malloc(1) at multibytecodec.c:1201 -> ASan trips.
- [repro] deterministic:
    d=codecs.getincrementaldecoder('hz')(); d.decode(b'~',False); d.decode(b'',True)
  realistic: list(codecs.iterdecode([b'~'],'hz'))
  Non-triggering (documented): b'~'.decode('hz'), TextIOWrapper.read,
  codecs.getreader('hz').read (single-shot over bytes buffer w/ NUL).
- [confirm] Full ASan reports saved: audit/findings/hz_asan.txt (min),
  audit/findings/hz_asan_iterdecode.txt (streaming). Both READ size 1, "0 bytes
  after 1-byte region", SUMMARY hz_decode _codecs_cn.c:417.
- [age] git blame: read hoisted above check since d949126995a7 (2013). File last
  touched 2023 (217911ede5d). Present on main @ 8f847875d60.
- [dedupe] gh search issues+PRs (12 queries) -> no match. Nearest: #101180
  (same class, iso2022, fixed there = wf-0036 evidence); #74189/PR#1556
  (HZ functional escape fix, 2017). New.
- [parent] workflow-0036 (speculative multi-element lookahead w/o proving next
  element in-buffer). Precise fit; see FINDING-001 doc.
- [fix] move REQUIRE_INBUF(2) before reading INBYTE2.

## Suite (context / negative result)
- Default `./python -m test` under ASan+UBSan: only sanitizer artifact was the
  benign asan.807 (test deliberately requests ~4EB alloc -> allocation-size-too-big;
  matches benign wf-0020 category, not an interpreter defect). 0 UBSan runtime
  errors. A handful of asyncio/timing test failures = ASan-slowdown flakiness
  (benign wf-0042). Expected: default suite is CPython's ASan-CI-covered path, so
  no NEW memory-safety findings there; the finding came from targeted hunting of
  the under-covered HZ codec incremental path.

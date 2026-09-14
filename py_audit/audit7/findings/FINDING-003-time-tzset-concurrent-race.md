# FINDING-003 — `time.tzset()` races on process-global timezone state (concurrent tzset)

- **Family / hypothesis:** workflow-0077 **Site 1** (concurrent contexts race on process-wide
  libc / module timezone state).
- **Status:** **CONFIRMED** (TSan, free-threaded build `taxoshop/cpython-tsan-ft:current`,
  HEAD e5d4fa28). **Apparently under-tracked:** NOT listed in the open umbrella
  python/cpython#127081 ("Thread-unsafe libc functions"), and NOT among the modules in the
  #149816 "22 free-threading race conditions" scan. Same *class* as #127081 (thread-unsafe
  process-global state) but no specific tz/time entry found — see dup analysis.

## Root cause
`time_tzset` (`Modules/timemodule.c:1182`) calls libc `tzset()` (mutating the process-global
`tzname[]`/`timezone`/`daylight` and the libc TZ database state) and then `init_timezone`
(`:1864`) republishes the module attributes and, on this build, calls `get_zone` (`:1773`)
whose `strncpy(zone, p->tm_zone, n)` reads a libc/heap timezone-name pointer. None of this is
serialized by a CPython lock. Two threads both calling `time.tzset()` (a documented, supported
API — e.g. after `os.environ['TZ']=...`) race:

- **Writer thread:** `tzset()`/`init_timezone` `malloc`s and overwrites the timezone name
  storage.
- **Reader thread:** another `init_timezone`→`get_zone` `strncpy` reads that same heap block;
  `tmtotuple` (`:490`, the `struct_time` builder used by `localtime`/`gmtime`) was also observed
  reading `tm_zone` concurrently.

⇒ torn/UAF read of the timezone-name buffer and a racing publish of module globals.

## Reproducer (no ctypes)
`repro/tsan/hyp/t0077_s1_tzset.py` — half the threads loop `os.environ['TZ']=...; time.tzset()`,
half loop `time.localtime()` / `time.strftime('%Z')`.
(Note: `repro/tsan/hyp/t0077_s1_tzset_reader.py`, a single tzset-writer vs. localtime-only
readers, was TSan-clean in one run — the sharp race needs ≥2 concurrent `tzset()` callers.)

## Sanitizer output (log `logs/t0077_s1_tzset.tsan.txt`, 6 warnings)
```
WARNING: ThreadSanitizer: data race
  Read of size 4 by thread T3:
    #0 strncpy
    #1 get_zone       Modules/timemodule.c:1773
    #2 init_timezone  Modules/timemodule.c:1864
    #3 time_tzset     Modules/timemodule.c:1182
  Previous write of size 8 by thread T1 (malloc, in another time_tzset)
  Location is heap block of size 20 allocated by thread T1
(also: read at tmtotuple Modules/timemodule.c:490 — localtime/gmtime struct_time builder)
```

## Duplicate analysis / disposition
libc `tzset` is inherently process-global and non-reentrant, so upstream may classify this as
"caller must synchronize" (as they did for `os.environ`/`setenv` in #127081). But unlike
`setenv`, `time.tzset()` is a normal library call and the read side reaches into `localtime`/
`strftime` conversion (`tmtotuple`). It is a plausible **addition to #127081** rather than a
standalone report. Recorded as a confirmed sanitizer result; if filed, attach to #127081.
Line numbers are from the image build (HEAD e5d4fa28); local checkout (7bfa97f4) differs.

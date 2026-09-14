# FINDING-002 — `locale.localeconv()` reads libc `lconv` raced by concurrent `locale.setlocale()`

- **Family / hypothesis:** workflow-0077 **Site 2** (concurrent contexts race on shared
  process-wide state — libc static buffers).
- **Status:** **CONFIRMED** (TSan, free-threaded build `taxoshop/cpython-tsan-ft:current`,
  HEAD e5d4fa28). **DUP** of open umbrella **python/cpython#127081** ("Thread-unsafe libc
  functions"), which lists both `localeconv()` and `setlocale` as **open, unfixed**.
- **Confidence the hypothesis was real:** the 0077-S2 writeup predicted this exactly, quoting
  the in-tree comment "hopefully, the localeconv result survives the C library calls". It does not.

## Root cause
`_locale_localeconv_impl` (`Modules/_localemodule.c:340`) calls libc `localeconv()` and then
reads the returned `struct lconv *lc` field-by-field (`locale_decode_monetary` at `:232` does a
`strcmp(loc, oldloc)`; the `RESULT_STRING`/`GET_LOCALE_STRING` macros `PyUnicode_DecodeLocale`
each `lc->...`). `lc` points into glibc's process-global locale storage.

`_locale_setlocale_impl` (`Modules/_localemodule.c:165`, `result = setlocale(category, locale)`)
mutates that same process-global storage — glibc `strdup`s the new locale name and rebuilds /
frees the category data that `lc`'s fields point into. Neither function holds any CPython lock
around the shared static; with the GIL disabled (or even released around these calls on the
default build) the localeconv reader dereferences storage the setlocale writer is freeing/
overwriting → data race and potential use-after-free of the `lc->...` strings.

## Reproducer (no ctypes)
`repro/tsan/hyp/t0077_s2_localeconv.py` — 4 threads loop `locale.localeconv()` (readers) while
4 threads loop `locale.setlocale(LC_ALL, "C"|"C.UTF-8")` (writers).

## Sanitizer output (log `logs/t0077_s2_localeconv.tsan.txt`, 69 warnings)
```
WARNING: ThreadSanitizer: data race
  Read of size 8 by thread T1:
    #0 strcmp
    #1 locale_decode_monetary  Modules/_localemodule.c:232
    #2 _locale_localeconv_impl Modules/_localemodule.c:340
  Previous write of size 8 by thread T8:
    #0 malloc
    #1 strdup
    #2 _locale_setlocale_impl  Modules/_localemodule.c:165
  Location is heap block of size 8 allocated by thread T8 (freed/replaced by setlocale)
```

## Duplicate analysis
Open umbrella **#127081** explicitly enumerates `localeconv()` and `setlocale` as thread-unsafe
(suggested fix: `nl_langinfo` substitution) — still open, no PR merged for these two. Sibling
libc functions in the same issue are already fixed: `getservbyname`/`getprotobyname` (PR #132750,
reentrant variants) and pwd/grp (PR #132748) — consistent with our clean TSan runs for
`socket.getservbyname`/`getprotobyname` and `time.localtime`/`gmtime` (localtime_r/gmtime_r).
So this is a **confirmed re-find of a tracked-but-unfixed** bug, not a new report.

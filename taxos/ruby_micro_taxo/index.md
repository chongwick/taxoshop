# CRuby bug instance reports

| Issue | Title | Sanitizer record |
|---|---|---|
| [#14357](ruby_14357.md) | thread_safe tests suite segfaults | Yes |
| [#15165](ruby_15165.md) | heap-use-after-free (READ of size 8) in obj_free (gc.c:2266) | Yes |
| [#16105](ruby_16105.md) | heap-use-after-free in String#sub! | Yes |
| [#18001](ruby_18001.md) | AddressSanitizer finding heap-buffer-overflow in iseq_peephole_optimize | Yes |
| [#19761](ruby_19761.md) | AddressSanitizer fails with Thread and Process | Yes |
| [#19994](ruby_19994.md) | Seemingly require causes segfault?? | Yes |
| [#20398](ruby_20398.md) | heap-buffer-overflow in numeric literal parsing | Yes |
| [#20402](ruby_20402.md) | Double-free in TestIseqLoad#test_stressful_roundtrip | — |
| [#20921](ruby_20921.md) | Use-after-free in constant cache | Yes |
| [#21304](ruby_21304.md) | heap-use-after-free of Array#hash via mutating hash method | Yes |
| [#21332](ruby_21332.md) | heap-use-after-free caused by mutating the set | Yes |
| [#21333](ruby_21333.md) | heap-use-after-free caused by rehash during update | Yes |
| [#21461](ruby_21461.md) | Heap-buffer-overflow in Prism when encoding magic comment is invalid and assignment is incomplete | Yes |
| [#21613](ruby_21613.md) | TestGc#test_exception_in_finalizer_procs and TestGc#test_exception_in_finalizer_method fail with ASAN | — |
| [#22196](ruby_22196.md) | Heap-use-after-free in `fiber_switch` with transfer-terminated async tasks on 3.4.10 | Yes |
| [#22253](ruby_22253.md) | Clang UBSan reports NULL/0 memcpy for eval scope locals | Yes |
| [#22254](ruby_22254.md) | [Prism] Clang UBSan reports NULL/0 memcpy while serializing empty strings | Yes |

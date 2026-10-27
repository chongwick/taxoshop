# Owned auxiliary state allocated during an operation or lifecycle transition is not released when the path completes without transferring ownership, causing the/

An operation or lifecycle transition allocates owned auxiliary state, then misses the required release or ownership handoff on a normal, empty-input, alternate, initialization, or teardown path. The result may be produced successfully, but the auxiliary allocation or reference remains retained.

## Precondition

A routine acquires temporary buffers, objects, references, or nested state whose ownership must either be transferred explicitly or released before the routine or lifecycle phase ends.

## Critical operation

The routine uses that state to construct a result, update a container, register a callback, initialize a subsystem, create an execution object, or complete teardown, then reaches a return or ownership boundary.

## Interference

The corresponding cleanup or ownership transfer is omitted, conditionalized incorrectly, or applied at the wrong boundary on one completion path.

## Invalid assumption

The implementation assumes that successful completion, insertion into another structure, garbage collection, interpreter shutdown, or later teardown will automatically reclaim state whose ownership was never correctly transferred or released.

## Failure

Each affected invocation leaves direct or indirectly owned allocations live; repeated operations accumulate retained memory, while one-shot lifecycle paths produce sanitizer-reported leaks at shutdown or teardown.

## Scope

The reports span conversion, iteration, registration, interpreter initialization, tracing, execution-object creation, threading, and embedding/test lifecycles. The shared pattern is an ownership-cleanup gap; it is broader than data-processing success paths and does not require every report to involve repeated successful operations or a confirmed fix.

## Search strategy

1. Trace every allocation, retain, or reference acquisition to an explicit release or ownership transfer on all return paths.
2. Check empty-input and zero-length branches for temporary buffers that are neither installed as owned state nor freed.
3. Verify that container insertion, callback registration, or object handoff clearly documents which side owns the reference afterward.
4. Audit initialization, shutdown, and teardown paths for auxiliary state that remains reachable after the owning operation completes.

## Evidence

- [#140120](../micro_taxo/gh_140120.md): A digest operation allocated nested temporary hashing state, produced its output, and returned without freeing the temporary components; repeated digest use exposed direct and indirect leaks.
- [#140272](../micro_taxo/gh_140272.md): A database-clearing loop received an owned key buffer for each item and omitted its release after successful deletion, with the error path also requiring cleanup.
- [#140442](../micro_taxo/gh_140442.md): Callback registration created a new argument container and failed to release the local ownership after packaging it into the registered callback, producing a shutdown leak.
- [#140474](../micro_taxo/gh_140474.md): Array construction allocated a temporary converted buffer; the empty-input branch completed without adopting the buffer or freeing it, so repeated construction leaked it.
- [#141044](../micro_taxo/gh_141044.md): A thread-related initialization and lifecycle path retained object graphs associated with configured thread behavior, leaving direct and indirect allocations reported at process completion.
- [#141372](../micro_taxo/gh_141372.md): Creating a profiling object under an alternate monitoring configuration left an object allocated during subsystem setup unreclaimed, yielding a direct leak report.
- [#141542](../micro_taxo/gh_141542.md): Tracing initialization allocated a large auxiliary block during thread execution and did not establish a cleanup path before the process ended, yielding a direct leak.
- [#142476](../micro_taxo/gh_142476.md): Executor creation involved conditional ownership between the created object, code storage, and tracing state; a missing or misplaced release caused retained executors, while an incorrect early release caused use-after-free, demonstrating the need for an exact ownership handoff.
- [#145204](../micro_taxo/gh_145204.md): An embedding configuration API returned an allocated empty list and created a configuration object, but the test path returned without releasing either, causing direct and indirect leaks.

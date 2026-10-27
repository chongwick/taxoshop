# Lifecycle ownership diverges across reusable isolated contexts

Reusable runtimes mix context-owned resources with process-global, legacy, or externally shared state. Teardown either omits owned auxiliary allocations or invalidates state still retained by another user, producing leaks or stale-state memory faults.

## Precondition

Multiple runtime contexts, repeated initialization, or external runtimes share objects, metadata, allocators, caches, or references whose ownership and lifetime are not explicitly associated with one context.

## Critical operation

A context is initialized, reused, finalized, or destroyed, and its teardown releases context-owned state or skips cleanup for auxiliary resources created during initialization.

## Interference

Other contexts, process-global legacy state, extensions, tracing structures, or external runtimes retain references to released state; separate cleanup paths also leave owned allocations reachable.

## Invalid assumption

Teardown is assumed to reclaim all relevant state automatically, or shared and legacy state is assumed to remain valid across context destruction without explicit ownership, cleanup, or lifetime coordination.

## Failure

The result is cumulative leaks and memory growth when cleanup is omitted, or invalid reads, assertions, use-after-free, bad frees, and crashes when surviving references outlive their backing state.

## Scope

Membership was manually restricted to the evidence listed below. This is a mixed cluster. Six reports primarily show omitted cleanup or process-global retention causing leaks; five show stale or prematurely freed state used by another context or runtime. The umbrella is lifecycle ownership mismatch, not a claim that every leak becomes a use-after-free or that all shared state is invalid.

## Search strategy

1. Trace every context-initialization allocation and reference to matching cleanup or an explicit ownership transfer on normal, failure, and teardown paths.
2. Search static, process-global, cached, interned, and legacy extension state for references to context-owned objects, metadata, allocators, or bookkeeping.
3. Exercise repeated initialization, subcontext destruction, and restart sequences while checking for both per-cycle leaks and reuse of stale state.
4. Inspect teardown ordering across contexts and external runtimes; verify shared objects remain alive until every retaining user releases them.
5. Audit tracing, callbacks, caches, and exported handles for invalidation or lifetime coordination before their owning context is destroyed.

## Evidence

- [#100773](../micro_taxo/gh_100773.md): Embedding and finalization left allocations behind, with analysis linking residual growth to extensions not fully associating state and cleanup with each runtime lifecycle.
- [#111339](../micro_taxo/gh_111339.md): A second runtime initialization reused metadata and interned keys surviving prior finalization, causing invalid object state and assertions during type setup.
- [#113055](../micro_taxo/gh_113055.md): Context destruction omitted allocator arenas and indexing structures allocated for that context, producing retained memory across repeated lifecycle cycles.
- [#113190](../micro_taxo/gh_113190.md): Shutdown skipped cleanup for globally retained deduplicated values, causing leaks across restart and exposing hazards when later cleanup invalidates external references.
- [#113576](../micro_taxo/gh_113576.md): Repeated embedded-runtime teardown left shared allocator state crossing lifetimes, leading to use-after-free and invalid-free reports when later contexts reused it.
- [#140301](../micro_taxo/gh_140301.md): Subcontext creation copied configuration and related auxiliary data, but destruction omitted its cleanup, causing direct and indirect leaks per repeated cycle.
- [#140404](../micro_taxo/gh_140404.md): Single-phase module initialization placed types, dictionaries, callables, and related objects in process-global state without a subcontext cleanup boundary, so they leaked.
- [#141372](../micro_taxo/gh_141372.md): An alternate monitoring setup allocated a singleton-like object during profiling setup without a corresponding release, yielding a direct lifecycle leak.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0014](../macro_taxo_before_hybrid/workflow-0014.md)
- [workflow-0034](../macro_taxo_before_hybrid/workflow-0034.md)
- [workflow-0045](../macro_taxo_before_hybrid/workflow-0045.md)
- [workflow-0046](../macro_taxo_before_hybrid/workflow-0046.md)
- [workflow-0094](../macro_taxo_before_hybrid/workflow-0094.md)

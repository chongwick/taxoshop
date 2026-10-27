# Optimized runtime state remains usable after its assumptions require invalidation

Optimized runtime state outlives or bypasses invalidation, so execution or optimization trusts assumptions invalidated by lifecycle, ownership, mutation, or re-entrant state changes. The members include stale specialized execution after teardown, invalid entries retained by reference cycles, missing invalidation dependencies for promoted values, subject-type mutation during callbacks, and instrumentation-induced optimization of polymorphic calls.

## Precondition

The runtime has specialized executable state, cached values, dispatch metadata, or inferred targets whose validity depends on subsystem state, object shape or type, ownership cleanup, or stable call-site observations.

## Critical operation

The runtime installs, retains, reuses, or enters the specialized path without ensuring that all relevant invalidation events detach it, or without providing revalidation and a safe generic fallback when specialization is no longer justified.

## Interference

A lifecycle transition disables optimization; cyclic ownership keeps invalid specialized entries reachable; mutable state changes without a dependency watcher; user code mutates an operation subject during conversion; or instrumentation changes specialization state while a polymorphic call site lacks a unique target.

## Invalid assumption

The specialized representation, cached value, dispatch type, executor metadata, subsystem state, or inferred callable remains valid and present merely because the optimized path was previously selected.

## Failure

An assertion, invalid metadata or field access, segmentation fault, null dereference, or abort occurs instead of invalidating the specialization, deoptimizing, bailing out, reloading state, or reporting a recoverable type error.

## Scope

This is a mixed-mechanism umbrella rather than a claim that all reports share one memory-lifetime defect. The common pattern is unchecked reuse of specialized or dispatch state after the condition that justified it has changed. One branch concerns teardown-time stale execution, one concerns ownership cycles retaining invalid entries, one concerns missing dependency tracking, one concerns re-entrant mutation, and one concerns an ambiguous optimizer result after instrumentation state changes.

## Search strategy

1. Check every specialized or cached runtime entry for complete invalidation when lifecycle state, object shape, mutable attributes, or instrumentation state changes.
2. Trace reference-linked specialized entries after invalidation and verify that obsolete entries are detached from executable state without conflating retention with use-after-free.
3. Inspect callbacks and conversion hooks between dispatch selection and execution for subject mutation, and require post-callback revalidation before using cached type or layout assumptions.
4. Check optimizer paths for polymorphic or ambiguous call sites and require a null, missing-target, or bailout path instead of unconditional assertions or dereferences.
5. Verify that subsystem shutdown and re-entry paths either invalidate retained specialized operations or safely skip optimization when the subsystem is disabled.

## Evidence

- [#140936](../micro_taxo/gh_140936.md): A suspended computation resumed during finalization and reached a specialized control-flow operation after optimization had been disabled, exposing an unchecked subsystem-state assumption.
- [#141648](../micro_taxo/gh_141648.md): Invalidation left specialized executable entries reachable because reference cycles prevented cleanup; the report’s mechanism is retention of obsolete state, not evidence that the entries were freed and then used.
- [#142276](../micro_taxo/gh_142276.md): A mutable attribute had been promoted to a constant without an invalidation dependency, so reassignment left optimized execution relying on an obsolete value and type assumption.
- [#142883](../micro_taxo/gh_142883.md): User-controlled operand conversion changed the operation subject’s type before the previously selected implementation ran, demonstrating missing revalidation across re-entrant mutation.
- [#148716](../micro_taxo/gh_148716.md): A tracing-state transition caused optimization of a type-unstable call site where no unique callable existed, and an unchecked missing-target assumption triggered an assertion.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0117](../macro_taxo_before_hybrid/workflow-0117.md)
- [workflow-0124](../macro_taxo_before_hybrid/workflow-0124.md)
- [workflow-0125](../macro_taxo_before_hybrid/workflow-0125.md)
- [workflow-0134](../macro_taxo_before_hybrid/workflow-0134.md)
- [workflow-0156](../macro_taxo_before_hybrid/workflow-0156.md)

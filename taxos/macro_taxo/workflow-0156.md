# A specialized runtime optimizer processes a hot polymorphic call site after instrumentation state changes, but assumes a single callable target was inferred.

Hot indirect-call optimization can encounter receivers with varying types and no uniquely inferable callable target.

## Precondition

A loop repeatedly invokes a method-like operation on receivers of incompatible types until the call site reaches the optimization threshold.

## Critical operation

The optimizer compiles the polymorphic call site and attempts to select a representative callable target.

## Interference

Instrumentation or monitoring is enabled and then cleared, leaving specialization state altered so the optimizer processes the unstable site instead of abandoning optimization.

## Invalid assumption

The optimization path assumes the inferred callable target is always present and does not handle a missing target.

## Failure

An internal null assertion fires, aborting the runtime instead of falling back or skipping optimization.

## Scope

This is a cautiously scoped pattern from a singleton report; the shared mechanism is the unchecked missing-target case at a polymorphic call site, while the exact instrumentation state transition may be implementation-specific.

## Search strategy

1. Check hot-call optimization paths for polymorphic receiver handling when no unique target can be inferred.
2. Trace specialization-state transitions across instrumentation enable/disable operations before optimization begins.
3. Search for unconditional dereferences or assertions on inferred callable targets without a missing-target fallback.
4. Verify that unstable indirect-call sites bail out safely when target resolution returns null or ambiguous.

## Evidence

- [#148716](../micro_taxo/gh_148716.md): The report shows a hot loop with varying receiver types, an instrumentation setup-and-clear sequence affecting specialization behavior, and an optimizer assertion when no callable target is available.

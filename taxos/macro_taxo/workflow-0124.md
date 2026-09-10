# Specialized execution paths for incompatible runtime shapes remain reachable after invalidation because cyclic references defeat cleanup, allowing stale paths—t

A dynamic optimizer retains shape-specialized execution paths after their assumptions are invalidated, and later dispatch can reuse those paths against incompatible execution data.

## Precondition

The runtime repeatedly specializes one operation for objects with incompatible layouts, producing linked specialized paths and side exits that retain references to one another.

## Critical operation

The runtime dispatches through a specialized path or executor entry embedded in executable state.

## Interference

Invalidation marks the path obsolete, but cyclic references prevent reference-count cleanup from removing or detaching the invalid path from executable state.

## Invalid assumption

Dispatch and layout-dependent operations assume that the retained specialized path is still valid and that its execution metadata matches the current object layout and bytecode state.

## Failure

The stale path misreads execution data or reaches inconsistent executor metadata, causing an invalid memory access or an internal assertion failure.

## Scope

This is a singleton-derived pattern. It is scoped to runtimes that attach specialized execution paths to mutable executable state and rely on cleanup of reference-linked paths during invalidation; the report does not establish a broader rule for all shape confusion or invalidation failures.

## Search strategy

1. Check whether invalidation can leave cyclically referenced specialized paths reachable from executable code.
2. Trace every specialized-entry dispatch after invalidation and verify that obsolete entries are detached before reuse.
3. Check layout-dependent operations for guards that validate the current object shape rather than only the shape captured during specialization.
4. Stress alternating incompatible object layouts with repeated invalidation and re-entry, and assert that stale specialized paths cannot execute.

## Evidence

- [#141648](../micro_taxo/gh_141648.md): The report demonstrates that shape-polymorphic execution can leave invalid specialized executors in executable state because reference cycles defeat cleanup; subsequent execution produces a segmentation fault or assertions involving out-of-bounds data and inconsistent executor metadata.

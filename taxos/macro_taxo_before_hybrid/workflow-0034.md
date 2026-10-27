# Process-global runtime or extension state retains interpreter-owned objects or metadata across interpreter teardown and reuse

Interpreter lifecycle bugs occur when object-bearing state is shared at process scope instead of being owned by each interpreter instance and cleaned up with it.

## Precondition

An embeddable runtime can create, destroy, and later recreate interpreter instances or subinterpreters, while a built-in or extension component stores interpreter-owned references, type metadata, caches, allocator state, or similar state in process-global or static storage without complete lifecycle ownership.

## Critical operation

The runtime initializes or imports the component, uses its objects or types, then finalizes the interpreter and later initializes another interpreter or destroys a subinterpreter.

## Interference

Finalization releases interpreter-scoped objects such as strings, dictionaries, module state, or allocator resources while the shared state remains populated and is later reused or repopulated.

## Invalid assumption

Process-global state is assumed to remain valid across interpreter lifetimes, or interpreter finalization is assumed to discover and release every reference held by legacy shared state.

## Failure

References and allocations survive teardown, producing leaks or cumulative memory growth; when stale state is reused, the result can be invalid reads, invalid frees, assertions, or crashes.

## Scope

The reports include both cumulative per-cycle leaks and one-time residual allocations, as well as stale-state memory-safety failures. The shared pattern is specifically object-bearing or validity-dependent process-global state crossing an interpreter lifecycle; it does not imply that every sanitizer leak is caused by repeated initialization or that all process-global state is invalid.

## Search strategy

1. Search for static or process-global variables that store object references, type metadata, caches, or allocator state.
2. Trace initialization and finalization paths to verify that every component-owned reference is associated with one interpreter and released before that interpreter is destroyed.
3. Exercise initialization/finalization twice and subinterpreter creation/destruction under leak and memory-safety instrumentation.
4. Inspect reusable built-in or extension types for metadata dictionaries, interned names, and other fields that survive teardown but reference interpreter-owned objects.
5. Verify that extension initialization provides explicit per-instance state and an explicit teardown path for all owned resources.

## Evidence

- [#100773](../micro_taxo/gh_100773.md): Repeatedly initializing and finalizing an embedded runtime exposed residual allocations; the analysis distinguishes one-time process-lifetime allocations from allocations recreated on each initialization and identifies incomplete migration of extensions to lifecycle-associated state as the relevant mechanism.
- [#104791](../micro_taxo/gh_104791.md): Leak detection during module checking was attributed to unresolved initialization and finalization work, with the implicated allocation originating from runtime activity that was not fully reclaimed by the lifecycle.
- [#111339](../micro_taxo/gh_111339.md): A static type retained metadata after finalization; a name owned by the finalized interpreter was invalidated, and the next initialization reused that stale metadata, causing an assertion or crash.
- [#113576](../micro_taxo/gh_113576.md): Importing an extension during two initialization/finalization cycles caused stale shared state to be accessed after teardown, yielding leaks and use-after-free or invalid-free reports; isolating the extension state per interpreter resolved the issue in newer versions.
- [#140404](../micro_taxo/gh_140404.md): Loading a single-phase extension in a subinterpreter leaked module-created types, dictionaries, callable objects, and related allocations because process-global state had no cleanup operation tied to subinterpreter destruction.

# CPython Macro Taxonomies

Macro taxonomies describe recurring mechanisms that span multiple issue-level
micro-taxonomies. They are intentionally overlapping: a race can also be a
lifetime bug, and a re-entrant callback can violate a bounds invariant.

## Pattern Families
- [Re-entrant callbacks and protocol methods](reentrant_callbacks.md): Python
  callbacks invalidate C state while a native frame still uses it.
- [Concurrent shared state](concurrent_shared_state.md): free-threaded access
  exposes missing synchronization, ownership, or iterator isolation.
- [Lifetime and teardown ordering](lifetime_and_teardown.md): objects are
  freed, retained, or destroyed in an order that violates their ownership
  contract.
- [Bounds and representation invariants](bounds_and_representation.md):
  unchecked sizes, indexes, operands, or layout assumptions reach native code.
- [Error-path cleanup and resource accounting](error_path_cleanup.md): partial
  initialization and exception paths lose references or native resources.
- [JIT and execution-state invalidation](jit_execution_state.md): optimized
  execution assumes bytecode, frames, or runtime metadata remain stable.
- [Sanitizer, build, and test infrastructure](sanitizer_infrastructure.md):
  sanitizers expose failures in build configurations, test harnesses, and
  diagnostic tooling.

## Reading Rule
Use a macro taxonomy to identify the mechanism first, then follow its linked
micro-taxonomies for the issue-specific reproducer, failure site, and evidence.

# Macro Taxonomy: Lifetime And Teardown Ordering

## Pattern
One subsystem owns an object while another subsystem retains a pointer,
reference, cache entry, or native handle. Teardown frees the object before all
consumers have released it, or cleanup happens twice. The same mechanism also
causes leaks when an owner is never reached during shutdown.

## Common Boundaries
- Subinterpreter and interpreter finalization.
- Extension object close, clear, and deallocation paths.
- Cache invalidation and borrowed-reference use across callbacks.
- Thread, SSL, and shared-memory resource teardown.

## Failure Shapes
- Heap use-after-free and double-free.
- Dangling cache or filename entry during finalization.
- LeakSanitizer report after a partial or skipped teardown.

## Defensive Rule
Make ownership explicit and teardown idempotent. Hold a strong reference while
using cross-subsystem state, invalidate consumers before freeing owners, and
ensure every initialization path has exactly one matching cleanup path.

## Representative Micro-taxonomies
- [#144172](../micro_taxo/gh_144172.md): tracemalloc retains a subinterpreter
  filename after interned-string cleanup.
- [#151046](../micro_taxo/gh_151046.md): temporary `memoryview` outlives its
  backing buffer.
- [#148382](../micro_taxo/gh_148382.md): borrowed decimal context survives a
  Python callback.
- [#140608](../micro_taxo/gh_140608.md): concurrent SSL teardown double frees
  handshake state.
- [#141044](../micro_taxo/gh_141044.md): thread stack configuration leaks
  lifecycle bookkeeping.

## Membership Rule
Group micro-taxonomies whose bug class is use-after-free, double-free, or
memory leak, especially when trigger and evidence involve `clear`, `close`,
finalization, destruction, cache invalidation, or shutdown.

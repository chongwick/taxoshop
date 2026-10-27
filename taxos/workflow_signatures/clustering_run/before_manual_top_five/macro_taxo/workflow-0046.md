# Auxiliary lifetime or version metadata remains apparently valid after the object, backing mapping, or hierarchy state it describes has changed.

A runtime maintains derived bookkeeping such as non-owning reference links, traversal bounds, lookup-cache entries, or version markers. A release, mutation, replacement, stack change, or incomplete hierarchy update leaves that metadata stale; a later traversal or lookup trusts it and uses state that is no longer live or current. The cluster includes both stale-pointer lifetime failures and stale-cache/version-invalidation failures.

## Precondition

Execution maintains auxiliary metadata that points to an object or cached value, describes a mutable backing store, or marks a derived lookup as valid without independently owning the referenced state.

## Critical operation

The referenced object is released, a stack or container range changes, a backing mapping replaces or removes a value, or version propagation across related objects fails or stops partway through.

## Interference

A fast path, alternate mutation path, deallocation path, or failed update omits the required unlink, bounds update, cache invalidation, dependent-marker update, or replacement ordering; later garbage collection, traversal, or lookup consumes the unchanged metadata.

## Invalid assumption

The code treats a reachable auxiliary slot, nonzero validity marker, or cache hit as proof that the referenced object is still alive and that the derived result still matches current state, even though the metadata does not itself establish ownership or complete invalidation.

## Failure

Traversal or lookup reads metadata from a released object, uses a stale cached value instead of the replacement, or combines inconsistent version state, causing use-after-free, invalid reference-count operations, corrupted results, memory corruption, or a process crash.

## Scope

The common pattern is stale auxiliary state, not leaked ownership. Issues 96572 and 101975 concern lifetime or traversal bookkeeping exposing released objects; issues 108253, 114106, 119462, and 140496 concern lookup-cache or version-marker invalidation, including direct backing-store mutation and hierarchy-ordering failures. The reports support this boundary for managed runtime metadata and do not establish a rule for every cache or every non-owning reference.

## Search strategy

1. Enumerate every non-owning pointer, cache entry, traversal bound, and validity marker and verify that its invalidation is coupled to release, replacement, removal, and stack or container-shape changes.
2. Audit all direct and indirect mutation paths for backing mappings and related objects; confirm that they clear dependent cache entries and validity markers before releasing or replacing cached values.
3. Verify that hierarchical or dependent version assignment updates prerequisites before dependents and leaves all failure paths in an explicitly invalid state.
4. Inspect optimized decrement, deallocation, tracing, and garbage-collection paths for skipped unlinking or stale range metadata that can expose freed entries to later traversal.
5. Check cache-hit and metadata-consumption paths for an independent ownership or current-version check before dereferencing the referenced object.

## Evidence

- [#96572](../micro_taxo/gh_96572.md): An optimized release path skipped removal from global tracing bookkeeping, so later bookkeeping access followed links in an object that had already been freed.
- [#101975](../micro_taxo/gh_101975.md): A frame traversal bound was not updated after a stack element was released, allowing garbage collection to inspect the freed element through stale frame metadata.
- [#108253](../micro_taxo/gh_108253.md): Changing or deallocating a function left a borrowed version-cache pointer until lookup read metadata from the freed function; the fix centralized version changes so the old cache slot is cleared.
- [#114106](../micro_taxo/gh_114106.md): Direct mutation of an underlying mapping bypassed type-cache invalidation, leaving a cached value usable after replacement released it and producing stale or corrupted lookup behavior.
- [#119462](../micro_taxo/gh_119462.md): Repeated dependent lookups exposed broken versioning invariants: a derived object could retain a seemingly valid marker when prerequisite version assignment failed or occurred in the wrong order, undermining method-cache invalidation and causing corruption or crashes.
- [#140496](../micro_taxo/gh_140496.md): Direct replacement in a backing mapping released the old member without invalidating the type lookup cache, so a later lookup dereferenced the freed cached value instead of using the replacement.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0014](../macro_taxo_before_hybrid/workflow-0014.md)
- [workflow-0060](../macro_taxo_before_hybrid/workflow-0060.md)

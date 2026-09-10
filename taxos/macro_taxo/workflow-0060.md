# A hierarchy-dependent cache stores referenced values under validity markers, but mutation paths can leave those markers or entries inconsistent with the backing

Incomplete cache invalidation across related objects allows a lookup to accept a stale entry whose referenced value is no longer valid.

## Precondition

A lookup cache derives results through a hierarchy or indirect backing store, records a marker or version for validation, and retains a reference to the returned value.

## Critical operation

A derived lookup validates or reuses the cached entry while a related object or backing mapping is being updated.

## Interference

The update bypasses, partially performs, or misorders invalidation and marker maintenance, leaving a cache entry or marker apparently usable despite changed underlying data.

## Invalid assumption

A present or nonzero validity marker is assumed to prove both that the cached result reflects current hierarchy state and that its referenced value remains alive.

## Failure

The lookup returns stale data and may dereference a released value, causing ownership corruption, use-after-free, or process termination.

## Scope

The shared pattern is limited to hierarchy- or indirection-dependent caches whose invalidation and referenced-value lifetime are coupled; the reports do not establish a rule for all cache implementations.

## Search strategy

1. Trace every mutation path for inherited or indirectly resolved values and verify that it invalidates all dependent cache entries.
2. Check whether cache-validity markers are assigned, cleared, and propagated atomically across bases and derived objects.
3. Search for direct mutations of backing mappings or metadata that bypass the normal invalidation routine.
4. Inspect cache-hit paths for raw or borrowed references whose lifetime is not independently protected after invalidation.

## Evidence

- [#119462](../micro_taxo/gh_119462.md): Repeated updates and derived lookups exposed an ordering violation in hierarchical version assignment: a derived object could retain a nonzero marker after assigning a marker to its base failed, causing later updates to skip required dependent-cache invalidation.
- [#140496](../micro_taxo/gh_140496.md): Direct mutation of an underlying mapping changed an inherited lookup result without going through the cache-invalidation protocol, so a later cache hit reused a stale reference after the old value had been released.

# Diagnostic intrusive-list cleanup bypassed by optimized destruction

An optimized last-reference release path is incompatible with builds that embed live-object tracking links unless it performs the same tracking teardown as the canonical release path.

## Precondition

A diagnostic or tracing configuration maintains an intrusive global collection of live objects, and each object must be unlinked from that collection before its storage is released.

## Critical operation

A specialized fast path drops an object's final ownership reference and invokes destruction directly.

## Interference

The fast path bypasses the normal release/deallocation wrapper that unregisters the object from diagnostic tracking.

## Invalid assumption

Direct destruction is assumed to be equivalent to the normal final-release path even when diagnostic tracking is enabled.

## Failure

The freed object remains linked in the live-object collection; a later tracking cleanup follows or updates its embedded links, reads freed storage, and triggers a heap use-after-free.

## Scope

Singleton cluster: this pattern is scoped to optimized final-release paths that bypass required diagnostic/tracing bookkeeping; the report does not establish behavior for unrelated registries or lifetime mechanisms.

## Search strategy

1. Audit optimized final-release paths that invoke destruction or freeing directly; require diagnostic deregistration before storage release.
2. Compare every specialized reference-count-to-zero path with the canonical deallocation path under all diagnostic build configurations.
3. Find intrusive links used by global live-object or allocation tracking, and verify every destruction path unlinks them before freeing the containing object.
4. Exercise sanitizer builds with diagnostic object tracking enabled so optimized destruction paths are covered.

## Evidence

- [#96572](../micro_taxo/gh_96572.md): A tracing configuration kept objects in a global tracking list, while an optimized final-reference path bypassed the normal unregistering operation; later tracking cleanup dereferenced the freed object's retained links, producing a sanitizer-detected heap use-after-free.

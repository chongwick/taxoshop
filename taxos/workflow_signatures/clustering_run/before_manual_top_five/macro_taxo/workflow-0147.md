# Ownership or representation invariants fail across managed-object boundaries

A runtime boundary propagates a field, object handle, raw storage reference, or object representation without preserving the ownership and validity invariants required by later consumers. The shared pattern covers both incorrect reference accounting and stale or externally corrupted state that survives into deferred use.

## Precondition

Code obtains a borrowed, newly created, cached, or raw handle, or accepts a managed object whose lifetime and representation invariants are not independently secured before storing or forwarding it.

## Critical operation

A conversion or aggregate builder applies the wrong ownership convention, a cleanup path releases a newly created value too early, a retained pointer outlives its backing storage, or unsafe memory writes corrupt a live object's metadata.

## Interference

The source or backing storage is freed, reference counts are over-decremented, or object metadata becomes invalid while the result, cache, pointer, or object remains reachable; later cleanup, finalization, metadata lookup, or serialization consumes that invalid state.

## Invalid assumption

The code assumes a borrowed value is owned, a newly returned value is safely borrowed, a retained pointer remains backed by live storage, or a managed object's header remains valid without explicitly acquiring ownership, preserving storage, or validating representation invariants.

## Failure

Later decrement, dereference, metadata access, or free operates on invalid ownership, freed storage, or corrupted representation, causing reference-count corruption, invalid free, use-after-free, heap out-of-bounds access, fatal crashes, or process termination.

## Scope

This mixed cluster includes ownership-accounting mismatches, premature release, stale freed storage, and deliberately corrupted live-object metadata. The common boundary is an unchecked lifetime or representation contract. Leaked ownership, stale access, and invalid object layout remain distinct mechanisms requiring different checks.

## Search strategy

1. Audit every conversion, reconstruction, reduction, cache, and aggregate-building boundary for borrowed or newly created values whose actual ownership differs from the cleanup convention.
2. Trace retained object pointers, field references, views, and raw storage addresses through source release, cache cleanup, finalization, mutation, and serialization; require an explicit lifetime guarantee.
3. Check every reference-stealing, decrementing, or ownership-transferring path against the provenance of each value, including compatibility, subclass, descriptor, exceptional, and repeated-conversion branches.
4. Inspect consumers of externally mutable or raw object representations and verify type, header, pointer, reference, and ownership invariants before deferred metadata access or dereference.
5. Exercise repeated construction and destruction, source teardown, finalization, and malformed-representation cases to distinguish over-release from stale-storage or corrupted-state failures.

## Evidence

- [#86863](../micro_taxo/gh_86863.md): A compatibility-selected conversion path repeatedly decremented a shared value that had not been transferred with ownership, eventually causing finalization to free non-heap storage.
- [#135636](../micro_taxo/gh_135636.md): External corruption changed a live object's header, after which a later reference increment read the already invalid object representation and triggered a heap use-after-free.
- [#135637](../micro_taxo/gh_135637.md): External writes corrupted live-object metadata, including during deferred access, and later metadata processing dereferenced the invalid representation and crashed.
- [#140634](../micro_taxo/gh_140634.md): An aggregate reconstruction path used a reference-stealing convention for a borrowed field, so repeated destruction over-decremented the field and corrupted allocator or reference-count state.
- [#140651](../micro_taxo/gh_140651.md): A reconstruction result retained a pointer to a value whose storage was released during cleanup, and later serialization read the freed object header.
- [#142783](../micro_taxo/gh_142783.md): An accessor treated a newly created result as borrowed and decremented it immediately, freeing it before subsequent cache operations used it.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0014](../macro_taxo_before_hybrid/workflow-0014.md)
- [workflow-0019](../macro_taxo_before_hybrid/workflow-0019.md)
- [workflow-0084](../macro_taxo_before_hybrid/workflow-0084.md)

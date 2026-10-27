# Ownership-bound cleanup paths fail to reclaim direct or nested allocations

Operations and lifecycle paths allocate owned data, but cleanup contracts differ across several mechanisms: destructor metadata can target the wrong field, owner destruction can be shallow, temporary ownership can be dropped on completion or error paths, and backend or helper cleanup can omit nested allocations. The common pattern is failure to discharge explicit ownership, not use of stale or freed state.

## Precondition

A container, configuration, operation, helper, or backend interaction acquires heap storage whose direct or nested components require explicit deallocation or ownership transfer.

## Critical operation

The code completes the operation, transfers or packages the state, clears the container, or destroys the owner through a destructor callback, release path, helper, or backend cleanup API.

## Interference

The cleanup contract is incomplete or mismatched: a destructor is registered for the wrong ownership position, only the outer object is released, a temporary or returned allocation is omitted on a success, empty-input, or error branch, or a backend bulk cleanup leaves embedded allocations unreclaimed.

## Invalid assumption

The implementation assumes that outer-object destruction, successful packaging or handoff, generic bulk cleanup, or short-lived process exit will recursively release every allocation associated with the state.

## Failure

Direct or indirect allocations remain live after the ownership boundary; repeated operations accumulate memory, while teardown, leak checking, or sanitizer-instrumented builds report leaks or fail despite otherwise successful work.

## Scope

This mixed cluster supports a higher-level ownership-cleanup pattern with distinct mechanisms: metadata mismatch, incomplete deep destruction, omitted local release or transfer, and backend-specific nonrecursive cleanup. The reports establish leaks and sanitizer-visible retention, not stale-pointer or use-after-free behavior; the older build report also contains allocations not proven to share the configuration-specific cause.

## Search strategy

1. For every heap allocation and ownership acquisition, trace success, empty-input, error, teardown, and process-exit paths to an explicit deallocation or documented ownership transfer.
2. Verify that destructor callbacks, release flags, and cleanup branches correspond to the actual fields and allocation owners, including containers with asymmetric or null-valued entries.
3. Inspect owner-destruction routines for shallow frees and confirm that nested strings, arrays, list elements, temporary substructures, and registration storage are released with matching allocators.
4. Compare backend and helper implementations of bulk reset, clear, digest, probe, or teardown operations against per-record or per-component cleanup to detect nonrecursive behavior.
5. Check APIs that return newly allocated buffers, references, tuples, lists, or configuration objects and ensure the caller releases each returned resource on every exit path.

## Evidence

- [#121390](../micro_taxo/gh_121390.md): A hash table stored heap-allocated keys with empty values, but destruction callbacks were assigned to the opposite ownership slots, so the keys survived table teardown.
- [#121847](../micro_taxo/gh_121847.md): A sanitizer-enabled build helper reported leaks at process exit; later discussion separated cosmetic short-lived runtime leaks from a newer configuration cleanup defect, supporting the broader boundary of incomplete helper or configuration cleanup rather than one single root cause.
- [#138756](../micro_taxo/gh_138756.md): Freeing a configuration wrapper omitted independently allocated string, list, and registration members, requiring deep member cleanup and matching allocation/deallocation handling.
- [#140120](../micro_taxo/gh_140120.md): A digest operation created temporary nested state and returned after producing its result without freeing all nested components, causing repeated sanitizer-visible direct and indirect leaks.
- [#140272](../micro_taxo/gh_140272.md): A clearing loop received an owned key buffer from an external allocation API and omitted its release on both normal and deletion-error paths.
- [#140442](../micro_taxo/gh_140442.md): Callback registration created a new argument tuple, packaged it into a callback, and failed to release the local reference after the handoff, leaving a shutdown leak.
- [#140474](../micro_taxo/gh_140474.md): An empty-input conversion branch allocated a temporary converted buffer but neither adopted nor freed it before completing, so repeated construction leaked the buffer.
- [#145204](../micro_taxo/gh_145204.md): A test caller received an allocated empty list and created a configuration object but returned without releasing either, producing direct and indirect leaks.
- [#150536](../micro_taxo/gh_150536.md): A platform-specific bulk history cleanup released outer records but did not free duplicated text fields, showing that backend cleanup semantics may not recursively reclaim nested allocations.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0065](../macro_taxo_before_hybrid/workflow-0065.md)
- [workflow-0067](../macro_taxo_before_hybrid/workflow-0067.md)
- [workflow-0094](../macro_taxo_before_hybrid/workflow-0094.md)
- [workflow-0161](../macro_taxo_before_hybrid/workflow-0161.md)

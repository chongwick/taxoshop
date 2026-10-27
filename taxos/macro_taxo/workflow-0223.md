# Failure cleanup acts on ownership or destructor state that was not established by the failed operation

Native error paths can cross an ownership or initialization boundary incorrectly: a failed call may leave an output value invalid, a partially initialized object may not satisfy its destructor's preconditions, or a container may already own a record despite a later registration failure. These distinct mechanisms turn recoverable initialization errors into invalid releases, duplicate releases, or cleanup-time dereferences.

## Precondition

Initialization performs native calls, allocations, parent linking, or container registration incrementally, while failure handling funnels partial state through cleanup that can release or destroy it.

## Critical operation

A later native operation, allocation, or secondary registration fails after some output, object state, parent ownership, or container ownership has been established.

## Interference

The failure leaves cleanup-relevant state ambiguous or partial: an out-parameter may be non-null but invalid, a destructor-required field may still be absent, or a parent/container may retain ownership independently of local cleanup.

## Invalid assumption

The error path assumes failed operations leave no releasable state, partial objects are already destructor-safe, and local cleanup remains the sole owner even after ownership was transferred or recorded elsewhere.

## Failure

Cleanup performs an invalid or duplicate release, or dereferences uninitialized state; the original recoverable error is replaced by a crash, heap corruption, or ownership-count corruption.

## Scope

The cluster shares an umbrella pattern of invalid assumptions during partial initialization cleanup, but the mechanisms must remain distinct: issue 100795 concerns an ambiguous failed out-parameter and an invalid release; issue 144984 combines unsafe destruction of partial state with duplicate parent reference release; issue 145301 concerns container-retained ownership after partial multi-key registration. This does not claim that all failed calls, destructors, or insertion paths are unsafe.

## Search strategy

1. Trace every initialization failure edge after a native output, parent link, or container insertion, and verify cleanup is based on confirmed ownership and success status rather than pointer presence alone.
2. Audit destructors for fields initialized later than object creation, and force failures at each intervening allocation to confirm partial objects can be safely destroyed.
3. Map ownership transfers and reference-count changes across secondary registration failures, checking whether a parent or container will release the same resource during teardown.
4. Review native API contracts for output-parameter state on error and prohibit releasing failed outputs unless validity and ownership are explicitly guaranteed.
5. Exercise allocation and registration failures under sanitizers or fault injection, verifying exactly one release per owned resource and propagation of the original error.

## Evidence

- [#100795](../micro_taxo/gh_100795.md): A failed native lookup could leave its output pointer in an unknown state, while shared error cleanup released it based on non-nullness; the correction prevents cleanup from freeing an output whose validity and ownership were not guaranteed on error.
- [#144984](../micro_taxo/gh_144984.md): A child object acquired parent ownership before later allocations completed; failure destruction could dereference a cleanup table that was still absent and independently decrement the parent again.
- [#145301](../micro_taxo/gh_145301.md): A record was successfully inserted under an initial key, then a later keyed insertion failed; local cleanup freed the record even though the ownership-tracking table still retained it and would free it during destruction.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0035](../macro_taxo_before_hybrid/workflow-0035.md)
- [workflow-0149](../macro_taxo_before_hybrid/workflow-0149.md)
- [workflow-0153](../macro_taxo_before_hybrid/workflow-0153.md)

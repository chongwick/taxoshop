# Heap-allocated auxiliary data is owned by a container, item, or failure object, with cleanup delegated to a destructor slot or release-control path.

A resource owner records or invokes cleanup behavior for dynamically allocated state.

## Precondition

Heap-allocated auxiliary data is associated with a longer-lived container or state object, and its ownership requires explicit release during removal, clearing, destruction, or error handling.

## Critical operation

The code configures the cleanup callback or passes the control flags/branch condition that determine whether the owned allocation is released.

## Interference

A cleanup slot is assigned to the wrong ownership position, or release-control logic is altered by an inverted condition or incorrect flag combination.

## Invalid assumption

The cleanup metadata and release controls are assumed to match the actual owner and allocation state, so the normal teardown path is expected to reclaim the data.

## Failure

Teardown or error handling omits the required deallocation, allowing owned allocations to persist and producing a memory leak or steadily increasing memory usage.

## Scope

The two reports share an ownership-to-cleanup mismatch, but not one narrowly limited to associative-container keys and values: one is a destructor-slot reversal, while the other includes release-condition, flag-combination, and error-path mistakes.

## Search strategy

1. Verify that each container destructor callback is assigned to the field matching the resource actually owned by keys, values, or entries.
2. Trace every cleanup and error path for heap allocations and check that release flags and conditional branches select deallocation exactly when ownership requires it.
3. Review bitwise flag composition at release call sites and confirm that independent cleanup permissions are combined with the intended operator.
4. Compare allocation ownership comments, initialization state, and teardown behavior for mismatches between the recorded owner and the code that frees the resource.

## Evidence

- [#121390](../micro_taxo/gh_121390.md): A table held dynamically allocated key records with intentionally empty values, but its destructor callbacks were reversed, so destruction did not free the owned keys until the callback positions were corrected.
- [#140306](../micro_taxo/gh_140306.md): Several cross-component cleanup paths used incorrect release controls or error-path ownership handling, causing allocated data to remain unreleased until conditional logic, flag composition, and failure cleanup were corrected.

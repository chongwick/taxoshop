# Initialization-failure reporting combines premature wrapper destruction with context retrieval through an incompatible object pointer.

When native resource creation fails, cleanup releases a newly created wrapper before diagnostics finish, while the reporting path may also receive a different object type than the context accessor expects. The resulting error path uses invalid lifetime or layout assumptions instead of returning the initialization error safely.

## Precondition

A wrapper is allocated before an underlying native resource is initialized, and failure can transfer control to diagnostic handling with both the wrapper and a separate reporting-context object in scope.

## Critical operation

Native initialization fails, after which cleanup releases the wrapper and the error-reporting call is prepared using a pointer whose actual object type may not match the context accessor's expected type.

## Interference

Diagnostic handling dereferences the released wrapper or reads context fields through the incompatible pointer while constructing the failure result.

## Invalid assumption

The code assumes cleanup has not ended the wrapper's lifetime and that related object pointers are interchangeable because they participate in the same operation, despite distinct ownership and layouts.

## Failure

Error reporting performs a use-after-free or an out-of-bounds/type-confused field access, causing sanitizer-detected memory failure or a crash instead of a recoverable initialization error.

## Scope

This is a cautiously scoped singleton pattern. Its shared umbrella covers two simultaneous mechanisms in one failure path—premature release and incompatible object-pointer use—without treating ownership loss as equivalent to type confusion. The evidence supports initialization-failure diagnostics specifically, not a broader rule about all cleanup or error-reporting code.

## Search strategy

1. Trace native-resource initialization failures through cleanup and verify that all diagnostic reads occur before the wrapper's final release.
2. Check every error-reporting context argument against the accessor's required object type and field layout; reject merely related objects as substitutes.
3. Inspect failure paths for aliases retained across decref, release, or destructor calls and ensure they are not dereferenced afterward.
4. Exercise forced native-initialization failures under memory and undefined-behavior sanitizers to distinguish lifetime errors from incompatible-layout reads.

## Evidence

- [#144833](../micro_taxo/gh_144833.md): The report documents one initialization-failure path where releasing the wrapper precedes context retrieval through its dangling pointer, while the accessor also receives a socket object where a context object is required; the fix reorders reporting before release and supplies the correct context object.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0014](../macro_taxo_before_hybrid/workflow-0014.md)

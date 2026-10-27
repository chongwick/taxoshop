# Incompatible function prototype at an indirect callback or slot boundary hidden by type erasure, casts, or dispatch metadata

A callback or slot implementation does not match the exact prototype selected by its registration interface. Erased storage, casts, or generated calling-convention metadata let it pass registration, but indirect dispatch invokes it under an incompatible parameter, return, or calling-convention contract.

## Precondition

An indirect callback or slot interface requires a specific parameter list, return type, signedness, or calling convention, while the supplied implementation uses a materially different function type.

## Critical operation

Register, store, or dispatch the implementation through the callback slot, table, method descriptor, or generated interface that defines the required prototype.

## Interference

Type-erased fields, explicit function-pointer casts, or flags and generated metadata select a call convention without preserving or validating the implementation's actual function type.

## Invalid assumption

Assuming that a function-pointer conversion, generic storage, or matching-looking argument layout makes incompatible function types ABI-compatible; signedness differences are only defects when they violate the selected convention.

## Failure

The runtime performs an indirect call through an incompatible function type, causing undefined behavior that may appear benign on ordinary targets but can be reported or terminated by function-type sanitizers, CFI, or runtimes that enforce indirect-call signatures.

## Scope

The umbrella pattern is an incompatible function type at an indirect callback or slot boundary. The reports differ in the mismatch dimension—receiver type, argument type or signedness, calling convention, or return type—and in how checking is bypassed. This does not imply that every signedness difference or every function-pointer cast is invalid; the defect exists when the eventual dispatch prototype and implementation are not compatible.

## Search strategy

1. Inspect every callback, slot, and method registration and compare the implementation prototype with the exact interface type, including return type and signedness.
2. Find void-pointer storage, explicit function-pointer casts, or wrapper omissions that suppress compile-time type checking.
3. Verify that dispatch flags, generated metadata, and calling-convention markers select the same argument layout and prototype implemented by the callback.
4. Run function-type, CFI, or equivalent indirect-call instrumentation through registration and every dispatch path.

## Evidence

- [#111178](../micro_taxo/gh_111178.md): Shows numerous object-operation and callback implementations using specialized receiver or otherwise incompatible prototypes while generic tables dispatch them through broader interface types; sanitizer instrumentation reports the indirect-call mismatches, and fixes make implementations conform or add compatible wrappers.
- [#132097](../micro_taxo/gh_132097.md): Shows generated dispatch flags selecting a call convention whose receiver prototype differs from the implementation, so normal generic dispatch passes the receiver under the wrong type; forcing the generated convention to match removes the runtime undefined behavior.
- [#134457](../micro_taxo/gh_134457.md): Shows that callback argument-width or signedness and calling-convention details must agree with the selected indirect interface; the report distinguishes valid convention-specific signedness from an actual mismatched callback prototype that triggers sanitizer diagnostics.
- [#156762](../micro_taxo/gh_156762.md): Shows a slot field stored through type-erased storage accepting an implementation with the wrong return type, after which garbage-collection dispatch calls it through the required slot prototype and indirect-call instrumentation detects the mismatch.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0043](../macro_taxo_before_hybrid/workflow-0043.md)

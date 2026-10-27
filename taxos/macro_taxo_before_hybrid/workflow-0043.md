# A callback implementation is registered through a generic callback or slot interface even though its concrete prototype differs in parameter types, return type,

An indirectly dispatched callback violates the prototype required by its registration interface; type erasure or casts allow the mismatch to compile, but dispatch through the declared interface invokes the function with an incompatible type and may trigger sanitizer, CFI, or runtime indirect-call checks.

## Precondition

A callback or slot interface specifies an exact function prototype, but the supplied implementation uses a different parameter type, return type, signedness, arity, or calling convention.

## Critical operation

Register or store the implementation in the callback slot, table, or function object used by generic dispatch.

## Interference

Type-erasing storage, generated metadata, flags, or explicit function-pointer casts suppress compile-time type checking while generic dispatch selects and invokes the callback according to the interface contract.

## Invalid assumption

Assuming that conversion through void storage or a function-pointer cast makes differing function types ABI-compatible.

## Failure

The runtime performs an indirect call through the interface prototype, producing undefined behavior that may be reported or terminated by undefined-behavior instrumentation, CFI, or a target runtime enforcing indirect-call signatures.

## Scope

The shared pattern is prototype incompatibility at an indirect callback boundary, not specifically object callbacks or one particular cast form. The reports differ in whether the mismatch involves receiver type, argument-count type, calling convention, or return type, and whether storage or an explicit cast hides it.

## Search strategy

1. Inspect every callback and slot registration and compare the implementation prototype with the interface typedef exactly.
2. Find casts, void-pointer storage, or generated wrappers that erase function-pointer type information.
3. Check dispatch flags and calling-convention metadata against the actual callback parameter list, return type, and signedness.
4. Run function-type, CFI, or equivalent indirect-call instrumentation over callback registration and dispatch paths.

## Evidence

- [#111178](../micro_taxo/gh_111178.md): Shows concrete callback functions using subtype-specific receiver types and related prototype differences while being assigned to generic callback interfaces, with sanitizer failures on indirect calls.
- [#132097](../micro_taxo/gh_132097.md): Shows dispatch metadata selecting a generic calling convention whose receiver parameter differs from the implementation's concrete receiver type, causing undefined behavior until the generated convention is corrected.
- [#134457](../micro_taxo/gh_134457.md): Shows that inconsistent argument-count types and calling conventions in externally supplied callbacks can violate the selected indirect-call prototype; the discussion also limits the pattern to actual convention mismatches rather than every signedness difference.
- [#156762](../micro_taxo/gh_156762.md): Shows a slot implementation with an incompatible return type being accepted through type-erased slot storage and later called through the required slot prototype, where sanitizer or CFI detects the mismatch.

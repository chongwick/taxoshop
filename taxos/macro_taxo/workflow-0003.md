# Signed left shifts used to construct packed or bit-oriented values can trigger undefined behavior before the intended representation is finalized.

Low-level code performs left shifts in a signed integer while building a packed value or transformed bit pattern, even though the intended result is an unsigned or fixed-width representation.

## Precondition

A valid execution path can supply a negative intermediate value or a nonnegative value whose shifted result exceeds the signed type's representable range.

## Critical operation

The code left-shifts that value while it is still signed, postponing conversion or relying on signed arithmetic to produce the desired bit pattern.

## Interference

Input-dependent values and ordinary startup or decoding paths reach signed-shift cases that violate the language's rules; sanitizer instrumentation exposes them even when the resulting machine-level bits appear usable.

## Invalid assumption

Signed left shift is assumed to provide predictable bit packing or wrapping, with unsigned conversion afterward making the operation safe.

## Failure

Undefined-behavior diagnostics are emitted during normal execution, such as interpreter startup, routine decoding, or test execution; behavior is not portable and may differ between instrumented and release builds.

## Scope

The shared pattern is signed left-shift undefined behavior in low-level bit construction. The reports differ in trigger: one uses negative operands, while the others use positive values exceeding signed range; they do not establish a broader claim about every packed-state encoder or about release-build behavior.

## Search strategy

1. Search for left shifts whose left operand has a signed integer type and trace whether valid inputs can make it negative or large enough to overflow.
2. Check packing, byte-accumulation, tagging, and scaling code for signed shifts performed before conversion to an unsigned or explicitly width-limited type.
3. Run undefined-behavior sanitizers through startup, decoding, and boundary-value paths, including all-ones and other values near the signed width limit.
4. Verify that shift counts and intermediate types are safe independently of the final cast or intended modulo representation.

## Evidence

- [#65128](../micro_taxo/gh_65128.md): The report records repeated diagnostics for left-shifting negative values and identifies a fix that converts negative numbers to an unsigned size type before shifting, supporting the signed-operand packing mechanism.
- [#95635](../micro_taxo/gh_95635.md): The report shows ordinary interpreter execution diagnosing a signed left shift whose positive result cannot be represented in the signed type, supporting that the pattern includes signed overflow, not only negative operands.
- [#96735](../micro_taxo/gh_96735.md): The report shows byte unpacking accumulating an all-ones value through a signed left shift that cannot be represented, supporting the packed-bit construction case and its dependence on boundary inputs.

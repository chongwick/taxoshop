# Unchecked floating-point demotion before representability validation

A floating-point value is converted to a bounded numeric destination before the implementation establishes that the value is representable there.

## Precondition

A floating-point result may exceed the destination type's range, or—for an integer destination—its integral part may be outside that range.

## Critical operation

The implementation performs the floating-point-to-destination conversion before an explicit range check or a defined saturating/conversion routine.

## Interference

The out-of-range conversion has undefined or otherwise implementation-dependent behavior, which can vary across platforms and compiler optimizations.

## Invalid assumption

The implementation assumes the converted value, or a value converted back to floating point, reliably preserves enough information to detect that the original value was out of range.

## Failure

Range errors can be missed or reported inconsistently, and the program may produce an invalid destination value or trigger sanitizer/compiler-dependent behavior.

## Scope

The two reports share the ordering and representability mechanism across both floating-to-integer and floating-to-narrower-floating conversions. The pattern is limited to destinations whose range does not represent every possible source value; it does not claim that all floating-point conversions are unsafe.

## Search strategy

1. Search for floating-point expressions cast to integer types before any explicit min/max bounds check.
2. Search for floating-point values narrowed to a smaller floating type before checking whether the source exceeds that type's finite range.
3. Inspect overflow checks that cast first and then compare the result after converting it back to floating point.
4. Trace rounding, scaling, splitting, or unit-conversion paths for conversions whose intermediate floating-point result can exceed the destination range.

## Evidence

- [#75554](../micro_taxo/gh_75554.md): The report's fixes add representability checks before conversions to integer and narrower floating types, replacing post-conversion/back-conversion checks that could themselves rely on undefined behavior.
- [#77756](../micro_taxo/gh_77756.md): The report identifies multiple sanitizer findings where out-of-bounds floating-point values were cast to other numeric types, notes compiler optimizations can change the prior behavior, and recommends defined conversion or explicit error handling.

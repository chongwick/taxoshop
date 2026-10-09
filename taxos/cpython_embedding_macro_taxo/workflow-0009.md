# Post-operation signed-size overflow checks in output-length calculations

Detecting overflow only after signed arithmetic has already formed an output size is unsafe when the detection relies on wrapped results or inverse arithmetic.

## Precondition

Input lengths or replacement counts can make a computed output length exceed the representable signed size range.

## Critical operation

The implementation calculates the output size with signed addition or multiplication before establishing that the operands fit.

## Interference

Signed overflow is undefined, allowing an optimizing compiler to assume it never occurs and eliminate or invalidate checks based on the resulting wrapped value.

## Invalid assumption

A post-operation comparison, or reversing a multiply by division, reliably detects signed overflow and remains valid under optimization.

## Failure

The size-limit error path is bypassed; the invalid size reaches subsequent allocation or output processing and can crash.

## Scope

Singleton cluster. The report supports this pattern for signed output-size arithmetic in text-building paths; it does not establish the behavior for unsigned arithmetic or every form of overflow check.

## Search strategy

1. Find signed output-length additions followed by comparisons between the new value and its prior value.
2. Find signed multiplications whose overflow check divides the computed product by an operand.
3. Require bounds checks against the signed maximum before every output-size addition or multiplication.
4. Audit compiler configurations that omit signed-wrap semantics for arithmetic-based overflow checks.

## Evidence

- [#73331](../micro_taxo/gh_73331.md): A large replacement or join result caused signed output-length multiplication or addition to overflow; checks based on reverse arithmetic or a post-addition comparison were defeated by optimization and led to crashes.

# Post-operation signed-size overflow checks invalidated by compiler optimization

A text-size calculation performs signed multiplication or addition before checking whether the result overflowed, allowing undefined signed-overflow semantics to defeat the validation and propagate an invalid size into memory operations.

## Precondition

A text-building path derives an output size from attacker-influenced or otherwise sufficiently large lengths, counts, or separators using signed integer arithmetic, and the build does not guarantee wraparound semantics for that arithmetic.

## Critical operation

The implementation executes the potentially overflowing multiplication or addition and only afterward tests the result by reversing the arithmetic, comparing it with a prior size, or applying a similar wrapped-result check.

## Interference

Because signed overflow is undefined under the applicable compilation assumptions, an optimizing compiler may assume the arithmetic cannot overflow and remove, simplify, or invalidate the post-operation check.

## Invalid assumption

The wrapped signed result is a reliable representation of overflow and can be inspected after the operation to decide whether allocation or copying is safe.

## Failure

The overflow condition is missed, so an invalid output size reaches allocation, construction, or copying logic and can cause a crash instead of a controlled size-limit error.

## Scope

This is a cautiously scoped singleton pattern based on one report covering multiple related text-size paths. It generalizes to signed output-size arithmetic whose validity check occurs after the arithmetic, but does not establish that every post-operation check is vulnerable or that unsigned arithmetic has the same mechanism.

## Search strategy

1. Find text or buffer output-size calculations that multiply or add signed lengths, counts, or delimiter sizes before checking bounds.
2. Identify overflow checks that divide the computed product, compare a new total with an old total, or otherwise inspect a result only after signed arithmetic has occurred.
3. Check whether the arithmetic relies on compiler wraparound behavior and whether the relevant build flags explicitly provide that guarantee.
4. Trace unchecked or incorrectly checked size values into allocation, buffer writes, copying, or concatenation paths and verify that overflow produces a controlled error.

## Evidence

- [#73331](../micro_taxo/gh_73331.md): The report documents signed multiplication and addition used to calculate replacement and joined-text sizes, with checks performed afterward through division or comparison against the prior size. It states that an optimizing compiler removed the broken checks when wraparound semantics were not enabled, leading to segmentation faults; fixes replaced

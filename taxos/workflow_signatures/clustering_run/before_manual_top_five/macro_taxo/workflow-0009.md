# Signed overflow in derived safety values defeats validation or bounded operation

A system derives a safety-critical size, duration, or deadline from large externally influenced quantities using bounded signed arithmetic. In one mechanism, overflow is checked only after multiplication or addition; in another, individually valid timeout operands are added to a current timestamp without checking the derived sum. Signed-overflow undefined behavior or an unrepresentable result then defeats validation or bounded operation.

## Precondition

A large or maximum-range input is accepted as valid on its own and participates in signed multiplication or addition to form a derived output size, absolute deadline, or similar operational value; the arithmetic does not guarantee defined overflow handling.

## Critical operation

The implementation performs the signed arithmetic before establishing that the complete derived value is representable, either by calculating a product or accumulated size and checking afterward, or by adding a relative duration to a current clock value.

## Interference

Signed overflow is undefined under the applicable compilation assumptions, allowing an optimizing compiler to remove or invalidate post-operation checks; where no such check exists, the raw overflow directly corrupts the derived value.

## Invalid assumption

A standalone limit on an input, or inspection of the wrapped result after signed arithmetic, is treated as proof that the derived size or deadline is safe and representable.

## Failure

Overflow is not handled as a controlled validation failure: an invalid size can reach allocation or copying and crash, while an invalid deadline can trigger undefined-behavior diagnostics or incorrect bounded-wait behavior.

## Scope

This mixed cluster supports a shared pattern of unsafe signed arithmetic in derived safety values, but the reports demonstrate two distinct mechanisms: post-operation checks defeated by undefined-overflow optimization for output sizes, and unchecked construction of an absolute deadline from otherwise valid timeout and clock values. It does not establish that every signed arithmetic check is compiler-vulnerable or that all failures are crashes.

## Search strategy

1. Find calculations that derive output sizes, durations, deadlines, or buffer capacities by multiplying or adding signed lengths, counts, timestamps, or timeouts.
2. Check whether operand limits are validated independently without proving that the complete derived arithmetic remains representable.
3. Identify overflow checks that inspect a signed result only after the multiplication or addition, including reverse-arithmetic and wrapped-result comparisons.
4. Trace derived values into allocation, copying, wait, retry, or deadline logic and verify that overflow is prevented before arithmetic or handled with checked, saturating, or otherwise defined operations.
5. Check whether retrying waits construct absolute deadlines by adding a relative timeout to the current clock and whether the addition clamps or rejects overflow.

## Evidence

- [#73331](../micro_taxo/gh_73331.md): The report shows signed multiplication and accumulated addition for text-output sizes, with overflow checks performed afterward through division or prior-size comparisons. It documents compiler optimization invalidating those checks when signed wraparound was not guaranteed, allowing bad sizes to reach string or buffer operations and cause crashes.
- [#77813](../micro_taxo/gh_77813.md): The report shows a maximum-valid nonnegative timeout being added to a nonzero monotonic timestamp in signed arithmetic, producing sanitizer-detected overflow. The remediation uses checked or clamping addition and deadline helpers, confirming that standalone timeout validation did not prove the absolute deadline representable.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0009](../macro_taxo_before_hybrid/workflow-0009.md)
- [workflow-0012](../macro_taxo_before_hybrid/workflow-0012.md)

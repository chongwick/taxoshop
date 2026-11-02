# A low-level instruction record is constructed with an operation whose contract disallows an operand, but the record carries a nonzero operand value.

A malformed operand supplied for an operand-free operation reaches low-level instruction construction, where an internal invariant is enforced by assertion rather than recoverable validation.

## Precondition

A caller constructs an instruction record for an operation that does not accept an operand and supplies a nonzero operand value.

## Critical operation

The instruction builder validates the record against the operation's operand contract using an internal invariant assertion.

## Interference

The caller-controlled malformed record reaches the internal builder without a public validation layer converting the contract violation into a recoverable error.

## Invalid assumption

The builder assumes callers always honor the operand contract, making process-terminating assertion failure an acceptable response to invalid input.

## Failure

The process terminates on an internal assertion instead of rejecting the malformed instruction through a recoverable argument or validation error.

## Scope

This is a cautiously scoped singleton pattern covering operand-contract violations during low-level instruction construction; the report does not support generalizing to other malformed instruction fields or all assertion failures.

## Search strategy

1. Check instruction builders for operand-free operations and verify that nonzero operands produce recoverable validation errors.
2. Check low-level constructors for assertions directly guarding caller-controlled operand fields.
3. Check public wrappers around internal instruction builders for missing argument validation.
4. Check call sites that construct operand-free instructions with nonzero operand values and verify their error handling.

## Evidence

- [#142661](../micro_taxo/gh_142661.md): The report demonstrates that supplying a nonzero operand to an operation that accepts none reaches low-level validation and triggers an internal assertion, terminating the process instead of raising a recoverable error.

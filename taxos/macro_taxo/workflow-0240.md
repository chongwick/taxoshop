# A nested-interpolation tokenizer updates delimiter-depth state for a closing delimiter before validating that the delimiter has a matching opener, allowing a-;

A nested-interpolation tokenizer updates delimiter-depth state for a closing delimiter before validating that the delimiter has a matching opener, allowing a malformed delimiter sequence to underflow parser state and trigger an internal invariant failure instead of a recoverable syntax error.

## Precondition

A tokenizer parses nested interpolation expressions whose delimiters may be mismatched or prematurely closed.

## Critical operation

When processing a closing delimiter inside an interpolation, the tokenizer decrements the current nesting-depth counter before checking whether a corresponding opener exists.

## Interference

Malformed nested or interleaved delimiters cause an unmatched closer to pass through the ordinary nesting-state update path, driving the depth below zero.

## Invalid assumption

Every closing delimiter encountered in the interpolation context has a matching opener, so the nesting-depth counter cannot become negative.

## Failure

The tokenizer violates its nonnegative-depth invariant and raises an internal assertion or aborts, rather than returning a syntax error that identifies the unmatched delimiter.

## Scope

This is a cautiously scoped singleton pattern supported by one report: it applies to tokenizers or parsers with nested interpolation and depth-based delimiter bookkeeping, and does not claim that all delimiter mismatches or all parser state errors share this exact failure mode.

## Search strategy

1. Inspect every parser or tokenizer path that decrements delimiter depth before validating a matching opener.
2. Check malformed nested-interpolation inputs containing extra closing delimiters and verify they produce recoverable syntax errors rather than invariant failures.
3. Trace whether delimiter bookkeeping is shared across nested interpolation modes and can be updated by mismatched delimiter kinds.
4. Assert that nesting counters are checked for underflow at the point where closing delimiters are consumed.

## Evidence

- [#122026](../micro_taxo/gh_122026.md): The report demonstrates that malformed nested interpolation with mismatched closing delimiters drove a delimiter-depth counter negative and triggered an internal assertion; the fix added an underflow check that returns an unmatched-delimiter syntax error.

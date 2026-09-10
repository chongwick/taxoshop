# Formatting adapters mutate formatter-produced text by removing a presumed trailing terminator without validating length or suffix.

A formatter-to-mutable-text adapter performs suffix cleanup on output whose emptiness and terminator presence are not guaranteed.

## Precondition

A formatter supplies text to an adapter that copies it into mutable storage; the formatter may legally or unexpectedly produce empty text or text without the adapter's expected trailing line terminator.

## Critical operation

The adapter accesses the final storage position and writes a string terminator there to remove the presumed trailing formatter terminator.

## Interference

Formatter output does not satisfy the adapter's assumed nonempty, terminator-suffixed representation.

## Invalid assumption

Every formatter result is nonempty and ends with the expected terminator, so indexing the final position and replacing it is always within bounds and semantically correct.

## Failure

Empty output can make the final-position index underflow and cause a heap-buffer-overflow before the allocation; nonempty output without the expected suffix can also have its final data byte incorrectly discarded.

## Scope

This is a cautiously scoped singleton pattern based on one report: it generalizes to formatter-output suffix cleanup, but does not establish that all terminator-removal bugs involve line-oriented text or heap storage.

## Search strategy

1. Inspect every formatter-output cleanup path for indexing at length minus one before checking that the length is nonzero.
2. Check whether suffix-removal code verifies the actual final byte or code unit before overwriting it.
3. Review adapters that convert immutable formatter results into mutable buffers for assumptions about mandatory trailing terminators.
4. Trace custom, alternate, or error-path formatters to determine whether they can return empty or unterminated output.

## Evidence

- [#143377](../micro_taxo/gh_143377.md): A formatting adapter copied formatter output into mutable storage, unconditionally treated the last position as a trailing newline, and wrote a null terminator there; empty output enabled an out-of-bounds heap write, while unterminated output required preserving the final data character.

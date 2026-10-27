# Recovery-time parser diagnostics use invalidated source context

Malformed input triggers both tokenization and grammar errors; recovery continues or retries parsing, leaving diagnostic source state inconsistent or unavailable before the final error is constructed.

## Precondition

Input can produce a tokenizer error together with a grammar error, especially when line-continuation-like markers interact with multiline or delimiter syntax.

## Critical operation

Parser recovery continues or repeats grammar parsing and constructs a final diagnostic from the tokenizer's current source buffer, line, and offset state.

## Interference

Recovery resets or mutates tokenizer state, may replace the earlier tokenizer error with a structural error, and may allow optional grammar branches to continue after a tokenizer failure.

## Invalid assumption

Grammar continuation and diagnostic construction assume that tokenizer errors have been propagated and that source-line and offset data remain valid and available after recovery.

## Failure

The parser crashes by dereferencing missing source data or reports an incorrect location instead of returning a recoverable syntax error.

## Scope

This pattern is supported by two closely related parser reports involving malformed continuation syntax and competing tokenizer/grammar errors. It generalizes the recovery and diagnostic-state interaction, not every parser crash or every malformed-input case.

## Search strategy

1. Trace every recovery or second-pass parse to verify that tokenizer errors prevent later structural diagnostics from using incomplete state.
2. Check optional and fallback grammar branches for continuation after a nested tokenizer error.
3. Inspect tokenizer error handling for mutation or replacement of shared source buffers before diagnostic construction.
4. Verify every diagnostic path validates source-line, buffer, and offset data before dereferencing or computing locations.

## Evidence

- [#89571](../micro_taxo/gh_89571.md): A malformed continuation-and-delimiter input causes an initial tokenizer error and a later structural error; recovery replaces the earlier error and diagnostic construction dereferences unavailable source-line data, causing a crash.
- [#89657](../micro_taxo/gh_89657.md): Malformed continuation input exposes the same tokenizer/parser error-state mismatch: optional grammar paths continue after a tokenizer failure and diagnostic source or offset state becomes invalid, producing a crash or incorrect error location.

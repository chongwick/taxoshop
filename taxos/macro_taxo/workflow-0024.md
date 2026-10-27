# Layered parser error paths continue after lower-level failure state becomes invalid

Malformed input causes a lower tokenizer or parser layer to report an error while a higher layer continues recovery, optional parsing, secondary diagnostic construction, or result packaging. The cluster includes two mechanisms: parser paths that reuse incomplete diagnostic context or attempt to replace an existing error, and tokenizer paths that treat an error-bearing sentinel as normal completion.

## Precondition

Malformed input produces a low-level lexical or parsing error together with partial token, source-location, delimiter, or parser state.

## Critical operation

A higher-level parser or tokenizer continues an alternative, recovery pass, diagnostic construction, or token/result construction based on the low-level return value.

## Interference

The lower-level error remains pending while recovery mutates or leaves source metadata unavailable, or while a sentinel value is indistinguishable from clean completion.

## Invalid assumption

Continuation and construction logic assumes the earlier error has been propagated or cleared and that source context and result data are valid, even when an exception remains pending or the returned sentinel represents failure.

## Failure

The system dereferences missing diagnostic data, overwrites or re-enters an existing error, asserts on an exception-bearing call, or emits a normal result with an error still set instead of returning the original recoverable syntax or tokenization error.

## Scope

This mixed cluster supports an umbrella pattern about failure-state propagation across layered tokenizer/parser and diagnostic code. Reports 89571, 89657, and 113602 concern secondary parser diagnostics or continuation with an existing or invalid error state; 140576 concerns sentinel/result confusion in tokenization. The evidence does not support claims about ownership leaks, stale or freed memory, or all parser crashes.

## Search strategy

1. Trace every recovery, retry, optional, and fallback parser branch to verify that it short-circuits when a lower-level error indicator or exception is set.
2. Audit all diagnostic constructors for validation of source text, line, offset, and delimiter context before dereferencing data that recovery may have reset or omitted.
3. Inspect every sentinel-handling path, especially end-of-input results, to distinguish clean completion from a sentinel returned with a pending error before constructing a token or wrapper result.
4. Check secondary error-reporting paths for attempts to replace or enrich an existing error, and verify that the first recoverable error is preserved.
5. Exercise malformed inputs that combine lexical failures with structural errors and assert that they return a diagnostic rather than crashing, asserting, or producing a normal result with an exception pending.

## Evidence

- [#89571](../micro_taxo/gh_89571.md): A lexical continuation error and an unclosed-delimiter condition caused a second parser pass to construct a structural diagnostic after recovery had left its source-line context unavailable, resulting in a null dereference; the fix preserves the earlier tokenizer error.
- [#89657](../micro_taxo/gh_89657.md): An invalid continuation error propagated through optional grammar branches that continued as if successful, leading diagnostic construction to use incorrect or unavailable source and offset state; fixes added error-aware unwinding and corrected locations.
- [#113602](../micro_taxo/gh_113602.md): A malformed structural input caused a later diagnostic attempt while the parser already had an active error, so diagnostic machinery invoked code with an exception pending and hit an internal assertion; the fix bails out when an existing error is present.
- [#140576](../micro_taxo/gh_140576.md): A low-level character read returned an end-of-input sentinel while setting an error, but tokenization treated it as clean exhaustion and built a normal token result, producing a system failure; the fix converts the error-bearing sentinel into an error token.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0023](../macro_taxo_before_hybrid/workflow-0023.md)
- [workflow-0047](../macro_taxo_before_hybrid/workflow-0047.md)
- [workflow-0103](../macro_taxo_before_hybrid/workflow-0103.md)

# Re-entering parser diagnostics while an earlier parse error remains pending can trigger an internal assertion instead of preserving and returning the original,0

A parser’s recovery or error-reporting path attempts to construct a new diagnostic after an earlier parse failure has already set the failure state.

## Precondition

Malformed structured input causes the parser to record a pending diagnostic and mark parsing as failed.

## Critical operation

A subsequent recovery or reporting branch invokes diagnostic construction or enrichment for the same input.

## Interference

The original diagnostic remains active while the later operation proceeds.

## Invalid assumption

The diagnostic-construction path assumes no prior error is pending and treats its operation as ordinary error-free execution.

## Failure

The runtime asserts or aborts during diagnostic construction, masking the original recoverable parse error.

## Scope

This is a cautiously scoped singleton pattern supported by one report: it applies to stateful parser diagnostic/recovery code where a pending error can coexist with a later diagnostic attempt, not to all forms of error overwriting.

## Search strategy

1. Check every parser recovery branch for diagnostic construction after a failure indicator is set.
2. Trace diagnostic helpers for calls that can allocate, invoke callbacks, or raise secondary errors while another error remains pending.
3. Verify that repeated or nested diagnostic creation preserves the first error or exits cleanly instead of replacing it.
4. Exercise malformed inputs that traverse multiple recovery alternatives and confirm they return a parse diagnostic rather than terminating internally.

## Evidence

- [#113602](../micro_taxo/gh_113602.md): A malformed input entered a parser error path, a later invalid-pattern diagnostic attempted to run while an error was already set, and the diagnostic machinery reached an assertion; the fix explicitly stopped diagnostic construction when the parser and error state were already active.

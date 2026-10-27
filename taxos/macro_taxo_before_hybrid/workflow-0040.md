# A test-suite environment-integrity check detects a process-wide environment mutation left behind by executed test or support code.

A test or support path mutates shared process environment state, and the mutation remains visible after that path completes.

## Precondition

The harness records or otherwise expects process-wide environment state to remain unchanged across test execution.

## Critical operation

Executed test or support code changes a process-wide environment variable or related environment state.

## Interference

The changed state persists beyond the responsible operation and affects the harness's post-execution comparison.

## Invalid assumption

The executed code is assumed to be environment-isolated or to restore the original state before returning.

## Failure

The harness reports an environment mismatch and marks the overall test run as failed.

## Scope

This is a singleton cluster. The report supports the residual-mutation and detection pattern, but does not identify the responsible routine, the specific environment state, or whether the mutation came directly from a test or from support code.

## Search strategy

1. Check every test and helper that writes process-wide environment state for restoration on all normal and exceptional exits.
2. Trace environment mutations across fixture, setup, teardown, and subprocess-boundary code to verify whether they remain in the parent process.
3. Search for end-of-suite baseline comparisons or environment-integrity assertions and identify which shared state they cover.
4. Review recently added or conditionally executed support paths that can run during broad test-suite jobs and confirm they cannot leak environment changes.

## Evidence

- [#109128](../micro_taxo/gh_109128.md): The report records a broad test run with one environment change detected and the result classified as an environment-change failure, supporting a residual process-wide environment mutation caught by suite-level integrity checking.

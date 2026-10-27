# A parallel, instrumented test environment causes a subprocess-based operation to return an unexpected non-success status, which the test harness surfaces as an;

A subprocess success check can expose environment-sensitive failures during parallel execution of instrumented tests.

## Precondition

Tests execute concurrently across multiple worker processes in an instrumented runtime or build.

## Critical operation

One test launches a subprocess to perform an isolated operation and requires that subprocess to complete successfully.

## Interference

Concurrent workload and instrumentation-related runtime conditions affect the subprocess execution path or its process termination status.

## Invalid assumption

The subprocess will always return the expected success status despite the surrounding parallel, instrumented execution conditions.

## Failure

The child exits with a non-success code, and the harness converts that unexpected status into an assertion failure.

## Scope

This is a singleton report. It supports the interaction between parallel instrumented execution, subprocess success assertions, and surfaced exit-status failures, but does not establish the underlying cause of the child’s non-success exit or a universal race-specific mechanism.

## Search strategy

1. Inspect parallel test runners for subprocess-based tests whose child exit codes are asserted to indicate success.
2. Check instrumented-build and race-detection configurations for tests that launch additional processes under concurrent load.
3. Trace subprocess creation and teardown paths for environment-sensitive exit codes that are reported only as generic assertion failures.
4. Verify whether tests distinguish infrastructure or instrumentation failures from ordinary child-process assertion failures.

## Evidence

- [#126445](../micro_taxo/gh_126445.md): A Linux test run executed many tests in parallel under a thread-sanitized/free-threading configuration; an import-related test launched a separate interpreter process, which returned exit code 66, and the helper reported that unexpected status as an AssertionError.

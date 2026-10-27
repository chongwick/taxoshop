# Sanitizer interception of deliberate worker-failure injection invalidates process-supervision tests

A process-pool recovery test deliberately crashes a worker during task handling, but sanitizer instrumentation intercepts the fault and terminates the worker through its own diagnostic path, so the supervisor/test harness observes sanitizer failure output instead of the intended worker-death condition.

## Precondition

A recovery test runs under memory-safety instrumentation and intentionally triggers a fatal memory signal inside a worker while decoding or executing a task.

## Critical operation

The worker performs the injected crash and the pool supervisor classifies the resulting process termination as a worker failure.

## Interference

The sanitizer intercepts the injected fault, emits a sanitizer fatal-error report, and aborts through instrumentation before the termination follows the test's expected observable path.

## Invalid assumption

The test assumes that deliberate fatal signals have the same process-level behavior and observable diagnostics under sanitizer instrumentation as they do in an ordinary runtime.

## Failure

The recovery test is reported as failed or produces unexpected sanitizer diagnostics instead of validating the intended worker-failure handling.

## Scope

This cluster contains one report, so the pattern is scoped to deliberate fatal-fault injection in supervised worker or subprocess recovery tests under sanitizer instrumentation; it does not establish that all sanitizer failures or all worker crashes behave this way.

## Search strategy

1. Find worker or subprocess tests that deliberately trigger fatal signals or invalid memory accesses, and inspect whether sanitizer-enabled runs are accounted for.
2. Trace how the supervisor distinguishes expected worker death from sanitizer-generated aborts and diagnostic output.
3. Search for crash-injection tests executed under memory-safety sanitizers without a runtime or test-harness guard.
4. Check whether assertions depend on exact process-exit behavior, signal status, or absence of sanitizer output when testing worker recovery.

## Evidence

- [#93981](../micro_taxo/gh_93981.md): A sanitizer-instrumented process-pool test intentionally triggered fatal memory faults during task decoding and worker function execution; the runtime emitted an AddressSanitizer fatal-signal report and aborted, and the affected recovery tests were reported as failed.

# Intentional crash stimulus conflicts with sanitizer signal handling

A worker-failure recovery test deliberately triggers a fatal signal, but sanitizer instrumentation treats that signal as a memory-safety crash rather than a transparent worker-termination event.

## Precondition

A worker-based recovery test runs under a memory-sanitized runtime and uses an intentional segmentation signal to simulate worker death.

## Critical operation

The worker raises the fatal signal while decoding a submitted task or executing task code.

## Interference

The sanitizer intercepts the signal, emits a fatal crash diagnostic, and aborts the worker through its own failure path.

## Invalid assumption

The test assumes its deliberate fatal signal will remain a controlled worker-death stimulus when sanitizer instrumentation is active.

## Failure

The recovery scenario produces sanitizer crash output and the affected worker-crash tests are reported as failed or otherwise do not follow their expected clean result path.

## Scope

Singleton cluster: the evidence covers intentional segmentation-signal recovery tests in worker processes under AddressSanitizer; it does not establish behavior for other sanitizers, termination mechanisms, or worker frameworks.

## Search strategy

1. Check worker-recovery tests for deliberate fatal-signal generation or invalid-memory crash helpers.
2. Check whether sanitizer-enabled test configurations run tests that intentionally crash subprocesses or workers.
3. Check whether expected worker-death assertions distinguish a sanitizer abort from the intended termination stimulus.
4. Check test output for sanitizer fatal-signal diagnostics emitted during intentional-crash scenarios.

## Evidence

- [#93981](../micro_taxo/gh_93981.md): A sanitizer-instrumented run reported failures in two worker-crash scenarios; the captured trace shows a deliberate segmentation signal during task decoding being handled as an AddressSanitizer fatal signal and abort.

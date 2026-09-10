# Instrumented worker crash wedges concurrent failure handling

A concurrently supervised worker can crash under diagnostic instrumentation, and the supervisor's crash-reporting path can wedge instead of converting the abnormal termination into a completed failure result.

## Precondition

A multithreaded test or service launches and waits for a worker process while sanitizer, fault-reporting, or equivalent diagnostic instrumentation is active.

## Critical operation

The supervisor performs a worker operation and relies on the worker's termination and diagnostic output to complete the supervision protocol.

## Interference

The worker crashes, transferring control into diagnostic crash handling that may block or fail to signal the supervisor's waiting path.

## Invalid assumption

The supervisor assumes that diagnostic handling remains progress-making after an abrupt worker crash and that it will always publish a terminal result or usable exit status.

## Failure

The parent waits indefinitely for completion, so the test or job hangs instead of reporting a recoverable worker failure.

## Scope

This is a singleton cluster. The report supports the crash-to-diagnostic-handling-to-hang mechanism, but explicitly leaves the exact diagnostic subsystem cause uncertain; the pattern is therefore scoped to instrumented subprocess supervision rather than all worker crashes.

## Search strategy

1. Inspect subprocess supervisors for waits that have no timeout or independent progress guarantee after abnormal worker termination.
2. Trace crash-reporting and diagnostic-handler paths for blocking I/O, locks, or joins inherited from a multithreaded parent.
3. Verify that worker crashes are translated into an explicit completion signal and failure result even when diagnostic output cannot be produced.
4. Review sanitizer or fault-instrumented subprocess tests for cleanup paths that depend on a crashed child performing normal shutdown.

## Evidence

- [#118729](../micro_taxo/gh_118729.md): The report documents an intermittent instrumented concurrent test hang, with analysis attributing it to a worker process crash followed by a possibly wedged fault-reporting path; the mitigation temporarily skipped the worker-crash-prone test until the underlying defect was fixed.

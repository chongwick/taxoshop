# Sanitizer-instrumented fork/thread lifecycle state is unsafe to treat as normal child state

Forking a sanitizer-instrumented process while threads are active can leave the child with instrumentation and runtime state for threads that no longer exist, making subsequent thread lifecycle or shutdown behavior unreliable.

## Precondition

An address/leak-sanitized process has active threads or thread-related runtime allocations when it enters a fork-sensitive lifecycle path.

## Critical operation

Create a child from that process and, before the child terminates, initialize another thread or run normal child shutdown.

## Interference

Only the forking thread survives in the child, while inherited thread stacks, allocations, and sanitizer synchronization or registration state remain associated with vanished threads.

## Invalid assumption

The child can safely create threads and perform ordinary shutdown/leak checking as though inherited per-thread state were live, valid, and reclaimable.

## Failure

Sanitizer runtime coordination can hang, or leak detection can report residual shutdown allocations and force an otherwise functional child to exit unsuccessfully.

## Scope

The direct orphaned-thread-state mechanism is established by the multithreaded-fork report. The other reports support the broader boundary: sanitizer-instrumented thread/process lifecycle paths can hang or convert shutdown diagnostics into failures; they do not establish that every reported shutdown leak has the same cause.

## Search strategy

1. Find forks reachable while non-caller threads are still live, and require thread quiescence or an alternate child-creation path.
2. Inspect post-fork child code for thread creation before exec or termination, and verify sanitizer-runtime compatibility.
3. Trace ownership and cleanup of inherited thread stacks, handles, locks, and sanitizer metadata in forked children.
4. Run fork-and-thread stress cases with leak detection enabled, and separate shutdown-only reports from allocations that grow per operation.
5. Check sanitizer-build child exit statuses independently from functional test results.

## Evidence

- [#89363](../micro_taxo/gh_89363.md): Address-sanitized process and concurrency tests intermittently hung during thread creation; debugging located a race in the sanitizer's thread-registration path, and affected tests were skipped as an external sanitizer problem.
- [#94064](../micro_taxo/gh_94064.md): Leak-sanitizer reports for thread-related lock allocations caused a forked child expected to exit successfully to exit with status 1; the discussion also distinguishes shutdown-only leaks from recurring operational leaks.
- [#140493](../micro_taxo/gh_140493.md): A direct reproducer forked while worker threads were alive, and the report explains that only the forking thread survives while other threads' stacks remain without cleanup, producing leak-sanitizer findings.

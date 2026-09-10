# Fatal-path diagnostics re-enter unsafe runtime state under thread instrumentation

A fatal-error reporter accesses runtime state or synchronization primitives from an instrumented, invalid, or signal-sensitive execution context, allowing the reporting path itself to fail or loop instead of terminating the process.

## Precondition

A test or fault intentionally enters the runtime's fatal-error path in a thread-instrumented build while the failing operation lacks the normal thread context or synchronization state required by the runtime.

## Critical operation

The fatal handler attempts to produce diagnostics by traversing runtime-managed state and acquiring its synchronization primitives.

## Interference

The instrumentation intercepts the fault through a signal or callback path and re-enters diagnostic handling while the original fatal path is already active or while runtime locks and thread state are unusable.

## Invalid assumption

Fatal reporting can safely inspect ordinary runtime data structures and acquire their locks from any fault context, including an instrumented signal path with no valid runtime thread state.

## Failure

The diagnostic path crashes recursively, spins, or blocks in synchronization code; the process hangs or consumes CPU instead of terminating with the expected fatal failure.

## Scope

This is a singleton cluster. The evidence supports a narrowly scoped pattern involving fatal diagnostics, thread instrumentation, and an invalid or unavailable runtime thread state; it does not establish that all crash reporters or all sanitizer builds deadlock. The observed outcome is platform-dependent: the same diagnostic defect may crash on one platform and hang on another.

## Search strategy

1. Check every fatal-error and crash-reporting path for traversal of runtime-managed containers or locks without a valid thread context.
2. Check whether sanitizer or signal callbacks can re-enter fatal reporting while the first diagnostic pass is still active.
3. Check intentionally crashing tests under thread instrumentation on every supported platform and verify that the subprocess terminates rather than hangs.
4. Check diagnostic code for ordinary locking, allocation, or runtime API calls that are unsafe during signal handling or after a fatal runtime invariant has been violated.

## Evidence

- [#120696](../micro_taxo/gh_120696.md): The report shows an intentionally invalid allocator call entering fatal handling in a thread-instrumented free-threaded build; diagnostic code then traverses runtime state, enters synchronization, and is re-entered through the instrumentation signal handler. On one platform this causes the reporter itself to crash, while on the affected platform it

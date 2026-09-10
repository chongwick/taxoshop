# Process duplication followed by thread creation can deadlock when an instrumentation or runtime subsystem retains non-fork-safe synchronization state.

A fork-like duplication of a multithreaded process is followed by worker or thread creation in the child, whose runtime instrumentation path depends on synchronization state inherited from the parent.

## Precondition

A multithreaded process can be duplicated while a runtime, allocator, sanitizer, or instrumentation subsystem is performing thread-related bookkeeping or holds an internal synchronization primitive.

## Critical operation

The duplicated child creates a worker or thread, entering the subsystem's thread-start or thread-registration path.

## Interference

The child inherits the subsystem's locked or incomplete bookkeeping state, but the parent thread responsible for releasing the lock or completing registration does not exist in the child.

## Invalid assumption

The child is assumed to inherit runtime instrumentation state that remains valid and recoverable after process duplication.

## Failure

Child thread creation blocks indefinitely inside the runtime or instrumentation layer, leaving the dependent operation, process, or test hung until timeout.

## Scope

Singleton cluster: this pattern is scoped to fork-like duplication of multithreaded processes followed by child thread creation when runtime instrumentation or support libraries maintain non-fork-safe synchronization state. It does not establish that ordinary application locks or every process-start method have the same failure mode.

## Search strategy

1. Inspect fork-like process-duplication paths for subsequent worker or thread creation in the child.
2. Check whether runtime, allocator, sanitizer, or instrumentation hooks run during child thread initialization.
3. Trace internal locks and registration flags across duplication boundaries, and verify that no vanished parent thread can be their only progress mechanism.
4. Search for child-side cleanup or reinitialization of runtime synchronization state after duplication.
5. Check whether affected operations are disabled, isolated, or replaced under instrumentation configurations known to be non-fork-safe.

## Evidence

- [#89363](../micro_taxo/gh_89363.md): The report documents intermittent hangs in fork-based multiprocessing and thread-related tests under address-instrumented builds; debugging shows the child-side thread-creation interceptor waiting for registration while another execution path is blocked on an internal instrumentation mutex, supporting a fork-inherited runtime synchronization deadlo

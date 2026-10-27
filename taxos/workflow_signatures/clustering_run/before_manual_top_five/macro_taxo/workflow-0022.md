# Forked child thread creation can deadlock in non-fork-safe runtime instrumentation.

A multithreaded process is forked under runtime instrumentation, and the child later creates a thread whose startup path enters instrumentation bookkeeping that was not safely reinitialized after the fork.

## Precondition

A multithreaded process uses an allocator, sanitizer, or instrumentation runtime with internal synchronization and can fork while that runtime has active thread bookkeeping.

## Critical operation

The forked child creates a worker or thread, invoking the runtime's thread-start, registration, or stack-initialization path.

## Interference

The child retains synchronization or registration state from the parent, while the execution context that could complete or release that state is absent or unable to make progress in the child.

## Invalid assumption

Forking is assumed to leave runtime instrumentation state valid for subsequent child-side thread creation.

## Failure

Child thread creation waits indefinitely in runtime initialization, causing queue, process, or executor operations to hang until timeout.

## Scope

Singleton cluster: the pattern is scoped to fork-like duplication of multithreaded processes followed by child thread creation under address-sanitizer-style runtime instrumentation. It does not establish the same failure for ordinary application locks, non-fork process starts, or uninstrumented builds.

## Search strategy

1. Inspect fork paths for child-side worker or thread creation under allocator, sanitizer, or instrumentation builds.
2. Trace runtime hooks invoked by child thread startup, including registration, stack discovery, and allocation bookkeeping.
3. Check every internal lock or completion flag crossing the fork boundary for ownership by a thread that will not exist in the child.
4. Verify whether child-side runtime state is reinitialized or whether affected operations are isolated under non-fork-safe instrumentation.
5. Reproduce fork-and-thread workflows with sanitizer instrumentation and capture stacks for both the blocked creator and the runtime bookkeeping path.

## Evidence

- [#89363](../micro_taxo/gh_89363.md): Address-instrumented fork workflows intermittently hang when child-side thread creation waits in the instrumentation interceptor for registration while another path is blocked on an internal allocator mutex, supporting inherited non-fork-safe runtime synchronization as the shared mechanism.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0021](../macro_taxo_before_hybrid/workflow-0021.md)

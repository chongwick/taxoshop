# Concurrent asynchronous notification delivery can reenter a mutable callback synchronously, causing unbounded callback nesting when no serialization or reentr\u

A callback registration is mutable while asynchronous notifications may be emitted concurrently and dispatched immediately on the receiving execution context.

## Precondition

A process-wide notification handler can be changed while another execution context emits notifications, and dispatch permits callback execution to overlap without a reentrancy guard or serialized queue.

## Critical operation

Perform repeated handler-registration changes or other long-running work while the notification source remains active.

## Interference

Rapid notifications arrive during an active handler invocation and the dispatcher invokes the same handler again before the earlier invocation returns.

## Invalid assumption

The handler will be invoked serially, or changing the registered handler will prevent an already-active notification stream from reentering it.

## Failure

Nested handler invocations grow until the runtime recursion limit is exceeded, aborting the workload with a recursion failure.

## Scope

This is a singleton-based pattern. The evidence supports concurrent notification delivery causing reentrant callback nesting and recursion exhaustion, but does not establish that every handler-registration change or every asynchronous dispatcher has this behavior.

## Search strategy

1. Check whether asynchronous callbacks can be dispatched synchronously while the same callback is still executing.
2. Check whether notification delivery has a serialization, queueing, coalescing, or reentrancy guard.
3. Check whether mutable process-wide handler registration is accessed concurrently with notification emission.
4. Check whether a handler can trigger or receive repeated notifications before its prior invocation returns.

## Evidence

- [#121065](../micro_taxo/gh_121065.md): A stress test that repeatedly changes a process-wide notification handler while another execution context emits notifications sometimes observed the handler recursively reentered hundreds of times, eventually exceeding the runtime recursion limit; the report also characterizes the behavior as flaky and specific to a concurrent/free-threaded mode.

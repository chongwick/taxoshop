# Concurrent evaluations lose process-wide pending-interrupt state through unsynchronized reset.

Concurrent execution contexts use a shared process-wide marker for an unhandled interrupt, but per-evaluation initialization can clear that marker while another context is recording or relying on it.

## Precondition

Multiple execution contexts can evaluate concurrently while unhandled-interrupt status is represented by shared process-wide state.

## Critical operation

One context records that an unhandled interrupt occurred for a later termination decision.

## Interference

Another context begins its evaluation and resets the same shared status as part of its initialization, without coordination with the first context.

## Invalid assumption

Per-evaluation reset is assumed to affect only the initializing evaluation and not erase state produced by another concurrent context.

## Failure

The later termination check observes cleared shared state, so the pending interrupt is not handled with the required termination behavior.

## Scope

This is a cautiously scoped singleton pattern covering shared process-wide pending-interrupt state cleared by concurrent evaluation setup; the report does not establish that every shared cancellation or termination flag has the same lifecycle or failure behavior.

## Search strategy

1. Search for process-wide interrupt, cancellation, or termination markers written by one execution context and read by another.
2. Check whether evaluation or initialization paths reset shared status that may have been set concurrently.
3. Check whether shared status updates, resets, and reads are synchronized or use an operation that preserves concurrent indications.
4. Trace termination decisions to confirm that a concurrent reset cannot erase a pending condition before it is consumed.

## Evidence

- [#128130](../micro_taxo/gh_128130.md): The report documents a race in which one concurrent evaluation records an unhandled interrupt while another evaluation clears the shared marker during initialization, allowing a later termination check to miss the pending interrupt.

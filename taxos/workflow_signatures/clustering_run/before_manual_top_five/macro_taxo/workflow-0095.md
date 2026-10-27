# Concurrent execution accesses process-wide state without a complete initialization, mutation, or lifetime protocol

Independent contexts or threads share runtime metadata, lazily initialized storage, mutable context registries, or resources, so their apparent isolation does not prevent conflicting process-wide accesses. The reports cover distinct variants: concurrent initialization, unsynchronized registry traversal, and concurrent resource close/use.

## Precondition

Multiple contexts or threads can run concurrently while process-wide state remains reachable during initialization, normal operation, registration, enumeration, or teardown.

## Critical operation

Code initializes or updates shared metadata, publishes or traverses a mutable context list, or reads or closes a shared resource through non-atomic access, incomplete locking, or an insufficient once/lifetime protocol.

## Interference

Another execution concurrently performs the same initialization or metadata update, changes the list while it is being inspected, or uses the resource while teardown closes it.

## Invalid assumption

Context isolation, prior initialization, an incidental lock or interpreter lock, or a lifecycle boundary was assumed to serialize all process-wide accesses and to keep shared state stable for the duration of its use.

## Failure

Race detection reports unsynchronized accesses; affected tests may be skipped or disabled, and execution may hang, time out, leak live threads, observe inconsistent metadata, or perform a concurrent close/use of a resource. A registry race does not by itself imply stale or freed state.

## Scope

This is a mixed cluster unified by incomplete coordination of process-wide state, not by one exact data structure or one failure mode. The reports distinguish concurrent lazy initialization, mutable-list traversal, and shared-resource lifetime races; thread-leak warnings are an observed consequence in one report, not evidence that every case involves leaked ownership or use-after-free.

## Search strategy

1. Search for process-global or static state initialized from multiple contexts; require immutable startup initialization, a once protocol, atomic publication, or a lock.
2. Check shared counters, flags, version metadata, aliases, and cached tables for atomic reads and writes, including assertions and debug reads outside the established synchronization boundary.
3. Check mutable thread, context, or resource registries for concurrent add/remove versus enumeration; require locking, a synchronized snapshot, or an explicit lifetime pin.
4. Check teardown paths for shared descriptors and other resources that can close while another context reads or uses them; verify ownership, reference, and close ordering.
5. Trace sanitizer skips, timeouts, and thread-leak reports back to the underlying shared-state access instead of treating suppression as synchronization.

## Evidence

- [#129824](../micro_taxo/gh_129824.md): Concurrent subinterpreters exposed several variants of the pattern: process-wide metadata and lazy initialization races, unsynchronized shared counters, and a descriptor close/read race; remedies included atomics, controlled initialization, and sanitizer-specific suppression for unresolved cases.
- [#140260](../micro_taxo/gh_140260.md): Independent subinterpreters concurrently executed extension initialization that wrote the same process-global optimization table, requiring a once-only or otherwise serialized initialization protocol.
- [#150284](../micro_taxo/gh_150284.md): Free-threaded activity concurrently enumerated a runtime-managed thread list while another thread registered a thread, producing a sanitizer race alongside hangs, timeouts, and thread-leak warnings; this supports mutable-registry synchronization without implying stale or freed state.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0077](../macro_taxo_before_hybrid/workflow-0077.md)

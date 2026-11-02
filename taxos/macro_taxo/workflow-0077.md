# Concurrent contexts access shared process-wide state without a complete synchronization or publication protocol

Concurrent isolated execution contexts are not fully isolated when they share runtime metadata, lazy initialization state, lifecycle state, flags, caches, registries, or resources.

## Precondition

The system allows threads or isolated contexts to run concurrently while process-wide or cross-context state remains accessible during initialization, normal operation, attachment, or finalization.

## Critical operation

A context reads, writes, initializes, publishes, clears, or closes shared state using plain access, incomplete locking, or an ordering assumption instead of a lock, atomic operation, once-only protocol, or fully synchronized publication.

## Interference

Another context concurrently performs a conflicting access, observes the state before initialization is complete, or uses the shared resource while it is being cleared or closed.

## Invalid assumption

Isolation boundaries, a global interpreter lock, a lifecycle phase transition, an incidental lock, or prior cleanup were assumed to serialize all shared accesses or make non-atomic fields safe.

## Failure

Race instrumentation reports unsynchronized accesses; affected tests may be skipped or disabled, and execution can additionally observe stale or inconsistent metadata, make incorrect decisions, use invalid resources, hang, or time out.

## Scope

The reports span subinterpreters, ordinary threads, free-threaded execution, and shutdown; the shared pattern is broader than the supplied isolated-context hypothesis. Some findings are value-benign or debug-only and some produce sanitizer failures without demonstrated user-visible corruption, so resource invalidation and hangs are possible outcomes rather than universal ones.

## Search strategy

1. Search for process-global, static, or runtime-owned variables read or written from code running in multiple threads or isolated contexts; verify a common synchronization protocol.
2. Check lazy initialization and cached-value paths for concurrent first use, especially writes to shared tables, slots, aliases, version data, or hash fields.
3. Check publication paths to ensure an object or thread/context record is not added to a shared registry before all fields read by other contexts are initialized.
4. Check finalization and shutdown paths for shared-state clears or resource closes that can overlap with daemon, attaching, blocked, or still-running contexts.
5. Check assertions, debug-only reads, and supposedly protected reads that occur immediately before acquiring the lock or stopping the world.

## Evidence

- [#129824](../micro_taxo/gh_129824.md): Concurrent subinterpreters exposed races in shared type metadata, version counters, exception aliases, runtime flags, module globals, and file descriptors; fixes used atomics, main-context-only initialization, static initialization, or sanitizer skips.
- [#130091](../micro_taxo/gh_130091.md): Runtime finalization deleted shared thread-local metadata while another thread was attaching and reading it; reordering the access until after the attach wait removed the race.
- [#130605](../micro_taxo/gh_130605.md): Concurrent executor activity exposed multiple races, including a configuration interval read while another thread updated it; atomic loads and stores were required before sanitizer tests could be re-enabled.
- [#133473](../micro_taxo/gh_133473.md): Highly concurrent queue activity exposed collector counters and thresholds being read and updated through incompatible access modes, causing sanitizer reports and potentially inconsistent collection decisions.
- [#140257](../micro_taxo/gh_140257.md): Interpreter finalization cleared shared evaluation state while daemon threads still performed atomic updates during acquisition, demonstrating that cleanup can overlap with supposedly finished contexts.
- [#140260](../micro_taxo/gh_140260.md): Separate subinterpreters concurrently initialized one extension's process-global optimization tables, so a once-only cross-context initialization protocol was required.
- [#150284](../micro_taxo/gh_150284.md): Free-threaded test activity produced a race while one context enumerated shared thread-list state and other threads changed it; the resulting sanitizer findings accompanied hangs, timeouts, and thread leaks.
- [#152741](../micro_taxo/gh_152741.md): A newly attaching thread was published to a shared thread list before its identity fields were initialized, allowing stop-the-world readers to race the publication-time writes.
- [#153014](../micro_taxo/gh_153014.md): A configuration/debug flag was written without synchronization while readers and the collector accessed it concurrently outside the stop-the-world region; relaxed atomic access was proposed.
- [#153852](../micro_taxo/gh_153852.md): The umbrella report records many residual free-threading races involving shared caches, lists, sockets, instrumentation, thread registries, and finalization, including benign-value races that still violate synchronization requirements.
- [#154822](../micro_taxo/gh_154822.md): A debug-only assertion read shared thread-list state before the operation that stopped the world, racing concurrent thread creation or exit; moving the read under the protection fixed the report.

# Concurrent unsynchronized access to shared mutable execution or native state

Multiple threads or asynchronous operations access one mutable record, context, container, pointer, buffer, or native state without a complete protocol covering conflicting accesses, state transitions, and required lifetime or cleanup ownership.

## Precondition

Shared mutable execution or native state is reachable by concurrent readers, writers, resetters, consumers, native calls, or cleanup paths.

## Critical operation

An operation reads, updates, publishes, consumes, validates, dereferences, or cleans up shared state while requiring coherent contents, stable lifetime, or exclusive ownership.

## Interference

Another operation concurrently writes, resets, replaces, resizes, clears, reinitializes, enters the same native context, or releases related state without the same effective synchronization, atomic publication, lifetime rule, or ownership protocol.

## Invalid assumption

A runtime guard, timing delay, one-sided atomicity, prior bounds check, borrowed reference, partial critical section, isolation boundary, or presumed exclusive cleanup is assumed to serialize all relevant accesses and preserve state or ownership.

## Failure

The overlap can produce a sanitizer-reported race, lost or contradictory state, invalid intermediate observations, out-of-bounds access, stale or freed-state use, double release, corruption, native-library failure, or a crash.

## Scope

This umbrella covers unsynchronized shared-state access. Members differ: ordinary or partially atomic races lose state; replacement, resizing, or reinitialization invalidates borrowed state; cleanup races can release an allocation twice. A matching audit must identify the actual access, lifetime, or ownership mechanism rather than treating all races alike.

## Search strategy

1. Search for shared mutable records, flags, pointers, containers, buffers, descriptors, registries, and native contexts reached by multiple threads; identify every reader, writer, resetter, and cleanup path.
2. Check that all related reads, writes, check-and-update sequences, and dependent fields use one complete synchronization or atomic-publication protocol, including test, debug, and representation paths.
3. Trace borrowed references, exported buffers, replaceable objects, resized storage, and native allocations to verify stable lifetime through the full use and exclusive or reference-counted cleanup.
4. Check whether locks or runtime guards are suspended or released during native calls, polling, callbacks, or blocking regions while the shared state remains in use.
5. Stress concurrent initialization, reconfiguration, reset, mutation, handoff, invocation, shutdown, and cleanup under race and memory-safety instrumentation.

## Evidence

- [#116912](../micro_taxo/gh_116912.md): A shared native descriptor field is written by close or detachment while another thread reads it during an operation outside the usual runtime lock, directly supporting an unsynchronized mutable-state race.
- [#128050](../micro_taxo/gh_128050.md): A lazily changed dispatch value is mutated during one call while concurrent calls read it, showing that fast-path publication or fallback changes still require a safe shared-state protocol.
- [#128100](../micro_taxo/gh_128100.md): A shared object-storage reference can be replaced while another operation reads through a borrowed reference, supporting the distinction between a data race and lifetime failure after replacement.
- [#128130](../micro_taxo/gh_128130.md): One concurrent evaluation records pending interrupt state while another evaluation resets the same process-wide marker during setup, so unsynchronized reset loses state.
- [#128144](../micro_taxo/gh_128144.md): Atomic publication on the writer side is paired with a plain reader, demonstrating that one-sided atomicity does not make a shared field access safe.
- [#130605](../micro_taxo/gh_130605.md): Concurrent executor activity reads configuration-related state while another thread updates it, requiring coordinated atomic access rather than ordinary loads and stores.
- [#130977](../micro_taxo/gh_130977.md): Independent aliases to one mutable byte storage perform concurrent reads and writes, directly supporting the shared-storage race mechanism.
- [#131325](../micro_taxo/gh_131325.md): A reusable buffer is handed to an asynchronous consumer before sequencing establishes exclusive use, allowing a later producer fill to overlap transmission of the earlier view.
- [#132886](../micro_taxo/gh_132886.md): A native descriptor race persists where the runtime lock was assumed to serialize access, supporting the need for coordinated access across configurations.
- [#140263](../micro_taxo/gh_140263.md): A worker atomically updates shared lock-state bits while a checker reads them non-atomically after sleep-based polling; timing does not synchronize the inspection.
- [#140608](../micro_taxo/gh_140608.md): Concurrent native handshake paths can both reach cleanup for the same allocation, supporting a distinct shared-lifetime and cleanup-ownership failure that manifests as double release.
- [#142717](../micro_taxo/gh_142717.md): Concurrent compound operations on one shared sequence mutate transient representation while other threads access it, causing invalid state and a memory-safety failure.
- [#143756](../micro_taxo/gh_143756.md): A runtime-level critical section is suspended across a released native region, allowing overlapping operations on one external context; full-operation serialization is required.
- [#144567](../micro_taxo/gh_144567.md): Concurrent process-wide locale changes replace and free returned storage while another thread decodes it, producing use-after-free from stale or freed state.
- [#145036](../micro_taxo/gh_145036.md): A lock-free inspection reads capacity and representation while concurrent resize or clear changes related metadata and storage, showing that atomic scalar reads do not stabilize the whole representation.
- [#145272](../micro_taxo/gh_145272.md): A replaceable reference field is read concurrently with replacement, requiring coordinated load or exchange and lifetime protection.
- [#146270](../micro_taxo/gh_146270.md): A check for absent state occurs outside the synchronized update, so concurrent deletion can report success more than once; this is a lost-linearization state error rather than necessarily freed-memory use.
- [#149142](../micro_taxo/gh_149142.md): Concurrent status and trap operations perform unsynchronized flag read-modify-write and clearing on one shared numeric context, requiring one common coordination protocol.
- [#149816](../micro_taxo/gh_149816.md): A reader validates an index, then concurrent reinitialization changes it before dereference, causing out-of-bounds access through check/use invalidation.
- [#150191](../micro_taxo/gh_150191.md): Multiple handshakes reuse one mutable native context whose internal state is not safe for overlap, producing an independent library-state race.
- [#151277](../micro_taxo/gh_151277.md): A comparison reads mutable external-library string storage while another operation replaces it, and library-internal synchronization does not cover both access paths.
- [#153014](../micro_taxo/gh_153014.md): A configuration or debug flag is written plainly while readers access it concurrently outside a stop-the-world region, supporting a value-benign but real synchronization defect.
- [#153852](../micro_taxo/gh_153852.md): Residual free-threading findings span shared caches, lists, sockets, instrumentation, registries, and finalization, supporting the broad umbrella while showing varied outcomes.
- [#153908](../micro_taxo/gh_153908.md): Representation reads a fast-path scalar or slow-path pointer plainly while writers update or replace it atomically or under a critical section, causing a race and possible stale-object use.
- [#153981](../micro_taxo/gh_153981.md): A representation path borrows a replaceable counter object while another path swaps and releases it, supporting the stale or freed-state lifetime submechanism.
- [#154524](../micro_taxo/gh_154524.md): A buffer pointer is read while resizing reallocates its backing storage, requiring both access synchronization and a lifetime rule for live exports.
- [#154756](../micro_taxo/gh_154756.md): An in-place ordering operation writes sequence slots while other threads iterate, supporting concurrent structural mutation versus read-only traversal.
- [#154821](../micro_taxo/gh_154821.md): Several related reference fields are read, replaced, or cleared during invocation, so partial synchronization leaves cross-field ownership and state transitions racy.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0056](../macro_taxo_before_hybrid/workflow-0056.md)
- [workflow-0075](../macro_taxo_before_hybrid/workflow-0075.md)
- [workflow-0077](../macro_taxo_before_hybrid/workflow-0077.md)
- [workflow-0081](../macro_taxo_before_hybrid/workflow-0081.md)
- [workflow-0095](../macro_taxo_before_hybrid/workflow-0095.md)
- [workflow-0107](../macro_taxo_before_hybrid/workflow-0107.md)
- [workflow-0150](../macro_taxo_before_hybrid/workflow-0150.md)
- [workflow-0152](../macro_taxo_before_hybrid/workflow-0152.md)
- [workflow-0157](../macro_taxo_before_hybrid/workflow-0157.md)
- [workflow-0158](../macro_taxo_before_hybrid/workflow-0158.md)

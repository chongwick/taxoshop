# Reusable isolated execution contexts allocate auxiliary state during initialization, but teardown releases only the primary execution state and omits some owned

Reusable isolated execution contexts allocate auxiliary state during initialization, but teardown releases only the primary execution state and omits some owned allocations such as allocator backing storage, lookup metadata, or copied configuration data.

## Precondition

A host repeatedly creates and destroys isolated execution contexts whose initialization allocates auxiliary memory associated with each context.

## Critical operation

The context is torn down and its ordinary execution state and context record are released.

## Interference

The teardown path does not invoke the corresponding cleanup for every auxiliary allocation made during initialization.

## Invalid assumption

Releasing the main context state, or relying on process termination or allocator reuse, is assumed to reclaim all context-owned memory automatically.

## Failure

Each create-destroy cycle retains some context-associated allocations, producing cumulative memory growth and leak-detector failures.

## Scope

The reports support incomplete teardown of context-owned auxiliary resources, not a rule about one specific allocator or configuration type. They do not establish that every retained allocation is isolated per context or that all memory growth is necessarily linear.

## Search strategy

1. Trace every allocation performed during context initialization and verify a matching release in every teardown path.
2. Check whether allocator backing stores, metadata tables, copied configuration, and dynamically duplicated strings outlive the context record.
3. Compare normal teardown with partial-initialization and initialization-failure cleanup for omitted ownership transfers or cleanup calls.
4. Run repeated create-destroy cycles under a leak detector and confirm retained bytes do not increase per cycle.

## Evidence

- [#113055](../micro_taxo/gh_113055.md): Repeated runtime or execution-context initialization allocated allocator backing arenas and auxiliary indexing structures that were not released during finalization, causing memory growth across cycles.
- [#140301](../micro_taxo/gh_140301.md): Repeated isolated-context creation copied configuration strings and lists whose cleanup was omitted before context deletion, producing direct and indirect leaks.

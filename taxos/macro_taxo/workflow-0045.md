# Pre-dispatch validation assumes current metadata on immutable executable artifacts

A runtime-wide monitoring update can leave immutable executable artifacts with stale or absent per-artifact metadata. If dispatch validates version consistency before selecting current per-artifact state or a runtime fallback, ordinary monitored execution can abort.

## Precondition

A runtime-wide monitoring configuration changes its version while previously created executable artifacts retain older metadata or lack a complete per-artifact monitoring structure.

## Critical operation

An event dispatcher handles an event for such an artifact and selects the tools or handlers using artifact-level monitoring state.

## Interference

The artifact metadata is stale or unavailable, including artifacts that cannot be eagerly rewritten after the global monitoring change.

## Invalid assumption

Dispatch assumes the artifact is current and safely validates it before refreshing metadata or choosing runtime-level fallback state.

## Failure

A version or consistency check fails, aborting the process during otherwise ordinary monitored execution.

## Scope

This is a cautiously scoped singleton pattern. It covers pre-dispatch validation failures involving versioned monitoring metadata on static or lazily refreshed executable artifacts; the report does not establish a broader rule for unrelated stale-state assertions.

## Search strategy

1. Trace runtime-wide monitoring-version changes and verify synchronization of already-created executable artifacts.
2. Inspect dispatch paths for version or consistency assertions that run before metadata refresh or fallback selection.
3. Check immutable or shared artifacts for lazy, stale, or absent per-artifact monitoring state after global configuration changes.
4. Verify that dispatch separates events requiring per-artifact data from events that can use runtime-level monitoring state.
5. Exercise configuration changes followed by events in previously created static or shared artifacts.

## Evidence

- [#106012](../micro_taxo/gh_106012.md): The report shows monitored execution aborting when an event reached a static code object whose instrumentation version differed from the runtime version; the fix moved validation into tool selection and added runtime fallback when per-code data was absent.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0039](../macro_taxo_before_hybrid/workflow-0039.md)

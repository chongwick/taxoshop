# Stale activation-record root boundary exposed during instrumentation callback

A runtime exposes an activation record to tracing or profiling while its cached boundary for traversable temporary values remains valid-looking instead of being invalidated for the callback interval.

## Precondition

An execution record contains temporary object references and a cached boundary that a memory collector uses to enumerate those references.

## Critical operation

Execution enters an instrumentation callback after publishing the record's current temporary-value state.

## Interference

During the callback interval, memory collection traverses the published execution record while a previously held temporary reference may already have been released.

## Invalid assumption

The collector assumes the cached boundary still identifies only live, safely traversable references, although the callback transition left that metadata stale rather than marking the temporary area unavailable.

## Failure

The collector dereferences a released object through the stale range, causing heap use-after-free and potentially a crash.

## Scope

Singleton cluster. Evidence supports this pattern specifically for collector-visible execution-record metadata across instrumentation-callback entry; it does not establish that all stale execution metadata or all callback transitions have the same failure mode.

## Search strategy

1. Check every tracing, profiling, debugging, and callback entry path invalidates or synchronizes execution-record root-range metadata before re-entrant collection can occur.
2. Audit temporary-value removal paths to ensure any collector-visible boundary is updated or made inaccessible before the reference can be released.
3. Find collector traversal routines that enumerate execution-record temporaries from cached bounds and verify their bounds cannot describe inactive storage.
4. Review transitions that publish an execution record to callbacks or other threads for stale root metadata left from the interrupted execution state.

## Evidence

- [#101975](../micro_taxo/gh_101975.md): A tracing or profiling entry path left a collector-visible temporary-value boundary valid; collection then traversed a released temporary reference, producing an intermittent heap use-after-free and possible segmentation fault. The accepted fix invalidated that boundary on callback entry.

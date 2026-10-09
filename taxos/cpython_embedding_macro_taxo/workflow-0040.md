# Sanitizer-visible lifecycle-boundary ownership mismatch

A short-lived process, runtime context, or embedded execution context allocates state whose lifetime is not fully aligned with its teardown boundary; instrumentation then exposes retained allocations, stale cross-context links, or missing sanitizer configuration.

## Precondition

A build helper, test subprocess, embedded runtime, or isolated execution context performs initialization that allocates nested, shared, global, or toolchain-owned state.

## Critical operation

The operation initializes, uses, and then exits or destroys that process or execution context.

## Interference

Teardown omits owned nested allocations, retains process-global state, leaves references to state being destroyed, or loses the sanitizer environment that normally governs leak reporting.

## Invalid assumption

The lifecycle boundary is treated as independently clean: ordinary teardown is assumed to release all relevant resources, preserve valid cross-context references, and retain the intended instrumentation policy.

## Failure

Leak detection fails an otherwise successful build or test, memory accumulates across lifecycle cycles, or teardown dereferences state whose owning context has already been destroyed.

## Scope

The direct copied-configuration teardown defect is specifically supported by issues 138756 and 140301. The full cluster is broader: it groups lifecycle-boundary failures exposed by instrumentation, including retained global state, teardown ordering errors, lost sanitizer configuration, and profiling-runtime allocations. It does not support claiming that all reports are configuration leaks or that every reported allocation is application-owned.

## Search strategy

1. Audit every owning destructor for dynamically allocated nested fields, lists, and copied configuration values.
2. Trace each copied per-context field through normal teardown and every partial-initialization error path.
3. Exercise repeated initialization and destruction under leak detection, including different destruction orders.
4. Check teardown of shared or process-global structures for links that still point into a context being destroyed.
5. Verify helper subprocesses preserve required sanitizer settings and distinguish application allocations from compiler or profiling-runtime allocations.

## Evidence

- [#104472](../micro_taxo/gh_104472.md): A test subprocess cleared its environment, removing the configured leak-detection suppression and turning pre-existing initialization allocations into an instrumented test failure.
- [#104791](../micro_taxo/gh_104791.md): A sanitizer-enabled build helper reported a residual allocation; discussion identifies incomplete initialization and finalization work as the relevant lifecycle area.
- [#113055](../micro_taxo/gh_113055.md): Repeated embedded initialization and finalization leaked allocator pages and retained runtime state after state began being recreated for each cycle; reports also document cleanup-versus-dangling-reference tradeoffs.
- [#116510](../micro_taxo/gh_116510.md): Destroying multiple isolated contexts in one order caused teardown to follow references to collection-list anchors already freed by another context, producing a crash.
- [#121847](../micro_taxo/gh_121847.md): A build-only helper triggered leak detection during startup and exit; follow-up distinguishes intentionally retained shutdown state from a later confirmed configuration-cleanup leak.
- [#138756](../micro_taxo/gh_138756.md): A public configuration owner released only its outer object while allocations made for nested scalar, list, and auxiliary configuration data remained unreleased.
- [#140301](../micro_taxo/gh_140301.md): Creating isolated contexts copied dynamically allocated configuration data, while the context destruction path failed to clear that copied configuration and leaked on repeated use.
- [#140404](../micro_taxo/gh_140404.md): Loading a legacy single-stage component in an isolated context leaked objects because its process-global state had no cleanup mechanism tied to context teardown.
- [#144199](../micro_taxo/gh_144199.md): Profiling instrumentation allocated bookkeeping during helper-process exit, and leak detection converted those external runtime allocations into build failures.

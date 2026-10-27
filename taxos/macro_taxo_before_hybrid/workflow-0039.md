# A runtime-wide instrumentation update invalidates lazily maintained per-artifact monitoring metadata, while event dispatch assumes that metadata is already at>>

A global monitoring-state change can leave immutable executable artifacts carrying an older metadata version. When dispatch reaches such an artifact, the dispatch path asserts version consistency before synchronizing or safely selecting current monitoring state, turning ordinary monitored execution into a process abort.

## Precondition

A runtime-wide monitoring configuration changes its version, but some immutable executable artifacts retain per-artifact instrumentation metadata from the prior version.

## Critical operation

An event dispatcher processes an event for one of those artifacts and selects instrumentation handlers or tool masks using the artifact's monitoring metadata.

## Interference

The artifact-level metadata is stale relative to the runtime-wide monitoring state, including cases where the artifact cannot be eagerly rewritten or has no complete per-artifact instrumentation structure.

## Invalid assumption

Dispatch assumes every artifact reached by an event has already been synchronized with the current runtime monitoring version and can therefore be checked before any refresh or fallback validation.

## Failure

A consistency assertion fails and aborts the process during otherwise ordinary monitored execution.

## Scope

This is a cautiously scoped singleton pattern supported by one report. It applies to versioned runtime instrumentation metadata on immutable or lazily refreshed executable artifacts; the evidence does not establish that every stale-metadata failure mode or every assertion-based dispatcher has the same cause.

## Search strategy

1. Trace every runtime-wide monitoring-version update and verify how existing executable artifacts are synchronized afterward.
2. Inspect event-dispatch entry points for assertions that compare artifact metadata versions before refresh, validation, or fallback selection.
3. Check immutable or shared executable artifacts for lazy instrumentation state that can outlive a global monitoring configuration change.
4. Verify whether dispatch distinguishes instrumented events from uninstrumented events before dereferencing per-artifact monitoring data.
5. Exercise monitoring configuration changes followed by execution of previously created artifacts, including static or shared artifacts.

## Evidence

- [#106012](../micro_taxo/gh_106012.md): The report documents a crash when an event reached code whose instrumentation version differed from the interpreter-wide monitoring version; the fix moved version and cross-check validation into tool selection and added runtime-level fallback for absent per-code data, supporting stale artifact metadata combined with pre-refresh assertion ordering.

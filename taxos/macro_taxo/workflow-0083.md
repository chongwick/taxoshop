# Startup-created runtime metadata survives an abbreviated interactive exit

A runtime that eagerly initializes built-in components can leave some startup allocations unreclaimed when an immediate interactive termination path bypasses complete teardown.

## Precondition

Run an eagerly initializing interactive runtime under allocation-leak instrumentation, then terminate it through an immediate or abbreviated exit path before ordinary interactive cleanup completes.

## Critical operation

Startup initializes built-in components and allocates their metadata, containers, and associated strings.

## Interference

The selected termination path performs incomplete or differently ordered shutdown, so some allocations made during startup are not released before process-exit leak checking.

## Invalid assumption

All interactive exit routes are assumed to execute equivalent cleanup for startup-owned component state, or startup allocations are assumed to be harmless process-lifetime objects.

## Failure

Leak instrumentation reports the residual startup allocations as leaks and can classify the process termination as unsuccessful.

## Scope

This is a singleton cluster. The report establishes an exit-path-sensitive startup-cleanup defect in one interpreter implementation and does not justify a broader rule about all interactive runtimes or all sanitizer configurations.

## Search strategy

1. Compare every interactive termination route and verify that each reaches the same complete runtime teardown sequence.
2. Trace startup allocations for built-in component metadata and strings to an explicit owner or shutdown release path.
3. Run leak instrumentation immediately after startup across normal, explicit, EOF, interrupt, and abbreviated exit paths.
4. Check whether process-exit leak reporting occurs before deferred runtime cleanup or finalizers can release startup-owned state.

## Evidence

- [#135618](../micro_taxo/gh_135618.md): Leak reports after immediate interactive termination identify allocations created while built-in components and their type metadata were initialized, including metadata containers and documentation strings; later comments show that other exit methods did not reproduce the report and that the behavior was fixed on the main branch.

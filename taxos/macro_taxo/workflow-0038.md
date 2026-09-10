# generalize evidence from singleton detailed bug analysis

A deliberately empty subprocess environment can remove sanitizer leak-suppression settings, exposing expected runtime-retained allocations as failures.

## Precondition

Run the environment-isolation test under leak-detecting instrumentation while the runtime retains initialization allocations until shutdown or intentionally does not reclaim them in the tested build mode.

## Critical operation

Launch a subprocess with an explicitly empty environment and initialize the runtime inside it.

## Interference

Clearing the environment also removes instrumentation configuration that suppresses known or expected leak reports.

## Invalid assumption

Assume that an empty application environment leaves sanitizer behavior unchanged and that all allocations surviving the test process are genuine leaks.

## Failure

The sanitizer classifies expected residual runtime allocations as leaks, causing the subprocess to exit unsuccessfully and the environment-isolation test to fail spuriously.

## Scope

This is a cautiously scoped singleton pattern for tests that intentionally launch a subprocess with no inherited environment under leak-detecting instrumentation. It does not establish that every empty-environment test or every sanitizer report is caused by expected runtime residual allocations.

## Search strategy

1. Check subprocess tests that replace the inherited environment with an empty mapping while running under sanitizers.
2. Trace whether sanitizer suppression or configuration variables are inherited, filtered, or removed before child-process startup.
3. Identify runtime initialization allocations that are retained until process finalization and compare them with leak-detector failure criteria.
4. Guard environment-clearing tests when their instrumentation configuration cannot survive the intentionally empty environment.

## Evidence

- [#104472](../micro_taxo/gh_104472.md): A singleton report shows that an empty-environment subprocess removed leak-suppression settings, allowing initialization-time runtime allocations that were otherwise suppressed to trigger an AddressSanitizer leak failure; the fix skips this test under the relevant sanitizer.

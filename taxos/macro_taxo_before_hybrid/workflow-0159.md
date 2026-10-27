# Fixed-depth recursion boundary tests become stale when build-time instrumentation or hardening changes effective recursion capacity.

A test assumes a hard-coded nesting depth will exceed the runtime recursion boundary, but build configuration changes the effective depth needed to trigger enforcement.

## Precondition

A recursive-boundary test uses a fixed nesting depth as a guaranteed value beyond the configured recursion limit.

## Critical operation

The test performs recursive processing at that fixed depth and asserts that the runtime raises its recursion-limit error.

## Interference

Compiler hardening or instrumentation changes per-level recursion behavior and resource consumption, so the same nesting depth no longer crosses the runtime guard.

## Invalid assumption

The historical fixed depth remains sufficient across materially different build configurations.

## Failure

The recursive operation completes without the expected limit error, causing the assertion to fail even though the runtime remains operational; increasing the tested depth restores the intended boundary condition.

## Scope

Singleton cluster: this pattern is cautiously scoped to deep-recursion boundary tests whose fixed depth becomes insufficient under compiler hardening or instrumentation; the report does not establish a broader rule for all instrumented test failures.

## Search strategy

1. Find recursive-boundary tests that use hard-coded nesting depths instead of deriving depth from the active limit.
2. Compare the effective recursion boundary under instrumented, hardened, and baseline builds.
3. Check that the test depth has sufficient margin above the configured limit for every supported build mode.
4. Re-run the boundary case with increased depth and measure whether the error is restored without unacceptable resource growth.

## Evidence

- [#150195](../micro_taxo/gh_150195.md): The report shows that a fixed deep-recursion depth stopped raising the expected recursion-limit error under a hardened build, and that increasing the tested limit/depth restored the intended condition; it also notes increased resource use for another deep test.

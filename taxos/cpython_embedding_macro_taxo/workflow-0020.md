# Instrumentation-induced fatal handling of deliberate oversized-allocation probes

A failure-path test deliberately requests an allocation beyond supported limits and expects the program to report an ordinary, recoverable allocation failure; an instrumented allocator instead terminates the process.

## Precondition

A test that exercises recoverable allocation failure runs under a memory-sanitizing allocator configuration that aborts on oversized allocations.

## Critical operation

The tested code issues a deliberately impossible or extremely large allocation request to trigger its allocation-failure path.

## Interference

The instrumentation layer intercepts the oversized allocation and treats it as a fatal allocation-size violation, aborting rather than returning an allocation-failure result.

## Invalid assumption

The test assumes that an allocation failure will be delivered to the program as a recoverable result regardless of the active allocator instrumentation and its failure policy.

## Failure

The process terminates before the test can observe or assert the expected recoverable allocation error.

## Scope

Singleton cluster. The evidence supports this pattern specifically for deliberately oversized-allocation tests under sanitizer allocator configurations with fatal default behavior; it does not establish that ordinary allocation failures or all instrumentation modes are unrecoverable.

## Search strategy

1. Find tests that deliberately request maximum-size, overflowed, or otherwise impossible allocations and assert a recoverable failure.
2. Check whether those tests run under instrumented allocator builds whose allocation-failure policy is fatal by default.
3. Verify that test eligibility guards detect every supported sanitizer configuration that aborts on oversized allocations.
4. For each oversized-allocation probe, confirm that the active allocator can return control to the program before asserting an error result.

## Evidence

- [#89359](../micro_taxo/gh_89359.md): An address-sanitized build aborted when allocation-failure tests made requests exceeding the sanitizer's supported size; the remediation excluded those tests under address and memory sanitizers because those allocators defaulted to aborting instead of returning an allocation-failure result.

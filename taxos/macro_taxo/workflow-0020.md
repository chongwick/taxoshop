# Stress tests use deliberately extreme allocations as if all allocators and runtime configurations will synchronously return a recoverable allocation failure, so

Extreme-allocation tests are coupled to allocator and runtime failure semantics that vary by platform and diagnostic configuration.

## Precondition

A test intentionally drives a computation into an infeasible memory allocation and expects allocation failure to be reported through the normal recoverable error path.

## Critical operation

The computation requests the extreme allocation and proceeds to depend on the allocator returning a failure indicator that the test can inspect.

## Interference

The active allocator, platform memory policy, or diagnostic instrumentation changes the outcome: the request may be accepted as virtual memory and fail only when touched, trigger an operating-system kill, or cause instrumentation to terminate the process instead of returning failure.

## Invalid assumption

The test assumes that an infeasible allocation is rejected immediately and consistently as a recoverable error across allocators, platforms, and instrumented builds.

## Failure

The process is killed or aborted before the expected error result reaches the test, so the test cannot validate graceful allocation-failure handling.

## Scope

This pattern is supported by two reports and covers the shared mismatch between extreme-allocation tests and environment-dependent failure semantics. The reports differ in mechanism—fatal instrumentation versus deferred allocation followed by OOM termination—so the pattern does not claim that every environment fails in the same way.

## Search strategy

1. Check tests that provoke allocation failure through intentionally extreme sizes and verify that the failure mechanism is explicit and deterministic.
2. Compare allocator, platform, overcommit, and instrumentation behavior before asserting that an allocation returns a recoverable error.
3. Inspect whether the test touches or materializes a huge allocation after the allocator call, which can convert deferred failure into process-wide OOM termination.
4. Verify that fatal diagnostic builds are skipped, isolated, or tested with subprocess exit expectations when allocation failure is expected to be recoverable.

## Evidence

- [#89359](../micro_taxo/gh_89359.md): The report shows that sanitizer-enabled builds convert an allocation that normally returns failure into a fatal crash, requiring such tests to be excluded or otherwise handled under those configurations.
- [#114331](../micro_taxo/gh_114331.md): The report shows that an alternate allocator on a particular platform accepts an enormous virtual allocation, then the process is killed when the memory is used, while another allocator returns failure earlier; the test therefore relied on non-portable allocation semantics.

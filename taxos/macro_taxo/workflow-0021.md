# Extreme-allocation tests assume environment-independent recoverable failure.

Tests that probe infeasible allocations depend on allocator and diagnostic configurations preserving the same recoverable failure semantics.

## Precondition

A test intentionally requests an infeasible allocation and expects the operation to report failure through the normal recoverable path.

## Critical operation

The computation performs the extreme request and relies on the active runtime and allocator to reject it in a form the test can inspect.

## Interference

Diagnostic instrumentation can turn allocation failure into a fatal abort, while an allocator may accept virtual address space and defer failure until memory is touched, allowing the operating system to kill the process.

## Invalid assumption

The test assumes every supported allocator, platform, and instrumented configuration rejects the request promptly and consistently as a recoverable error.

## Failure

The process aborts or is killed before the expected failure result can be checked, so the test itself becomes unreliable across environments.

## Scope

This two-report pattern covers one shared test-design mismatch with two distinct mechanisms: fatal diagnostic handling and deferred allocator or operating-system failure. It does not claim that all environments fail through the same mechanism.

## Search strategy

1. Inspect tests that provoke infeasible allocations and verify that the expected failure mode is explicit and deterministic.
2. Compare allocator, platform, overcommit, and diagnostic-build behavior before asserting recoverable allocation failure.
3. Check whether an accepted large allocation is later materialized or written, allowing deferred failure to become process-wide OOM termination.
4. Verify that fatal diagnostic configurations and platforms with different allocation semantics are skipped, isolated, or tested through subprocess outcomes.

## Evidence

- [#89359](../micro_taxo/gh_89359.md): The report shows that memory and address instrumentation abort on allocation failure instead of returning a recoverable failure, so extreme-allocation tests must account for fatal diagnostic semantics.
- [#114331](../micro_taxo/gh_114331.md): The report shows that one allocator accepts an enormous virtual allocation and the process is later killed on use, while another allocator rejects it; the test therefore relied on non-portable allocation timing and semantics.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0020](../macro_taxo_before_hybrid/workflow-0020.md)

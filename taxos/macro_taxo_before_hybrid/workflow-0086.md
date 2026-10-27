# A deep-recursion test runs under a memory-safety instrumentation mode that its skip guard does not recognize.

A compatibility guard for unusually deep recursive workloads omits the active instrumentation category, allowing the workload to execute under instrumentation that cannot tolerate its stack depth.

## Precondition

A test intentionally performs unusually deep recursion and includes conditional skipping for selected instrumentation modes.

## Critical operation

The test runner executes the recursive workload with memory-safety instrumentation enabled.

## Interference

Instrumentation increases effective stack consumption or otherwise reduces the usable stack available to the recursive workload.

## Invalid assumption

The skip guard assumes its existing instrumentation checks cover every mode that makes the deep-recursion test unsafe, but it does not account for the active memory-safety instrumentation category.

## Failure

The recursive workload exhausts the instrumented process stack, causing a sanitizer-reported stack-overflow abort and test failure instead of being skipped.

## Scope

This is a singleton cluster, so the pattern is scoped to deep-recursion tests whose instrumentation-compatibility guards omit a stack-impacting memory-safety mode; it does not establish that all sanitizer failures arise from missing skip conditions.

## Search strategy

1. Check deep-recursion or stack-depth tests for skip guards that enumerate instrumentation categories.
2. Verify that every memory-safety instrumentation mode affecting stack usage is represented in the guard conditions.
3. Search for recursive workloads that are expected to run only in uninstrumented or selectively instrumented configurations.
4. Inspect sanitizer-specific test failures for stack-overflow aborts before changing recursion limits or test logic.

## Evidence

- [#135830](../micro_taxo/gh_135830.md): The report shows a deep recursive test failing with an instrumented stack overflow, while its existing skip guard covers other sanitizer modes but not address instrumentation; the accompanying analysis proposes adding the missing address-mode condition.

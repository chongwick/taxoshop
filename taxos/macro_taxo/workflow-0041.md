# A low-level profiling or tracing hook is active when an instrumented process is duplicated; the child then re-enters the hook using inherited runtime state that

Inherited low-level profiling state is not reliably safe after process duplication in sanitizer-instrumented runtimes.

## Precondition

A process runs low-level profiling or tracing machinery and is built or executed with memory-safety instrumentation before duplicating its process image.

## Critical operation

The duplicated child continues execution through the profiling or tracing path using state inherited from the parent.

## Interference

Process duplication preserves hook-related state while the sanitizer changes memory, allocator, or runtime behavior and can expose unsafe post-duplication interactions.

## Invalid assumption

Profiling state established before duplication remains valid and fork-safe in the child.

## Failure

The child intermittently terminates with a sanitizer-detected memory-safety failure, causing the workflow or test to fail.

## Scope

This is a cautiously scoped pattern from a singleton report. The evidence establishes an intermittent sanitizer-dependent crash in a process-duplication profiling workflow, but does not justify a broader claim about all profiling implementations or all forms of process duplication.

## Search strategy

1. Check whether process duplication can occur while low-level profiling, tracing, unwinding, or trampoline state is active.
2. Trace every profiling hook and runtime-owned pointer used by the child after process duplication.
3. Check whether post-duplication child execution reuses allocator, thread, signal, or instrumentation state initialized only in the parent.
4. Run process-duplication tests under address, memory, and undefined-behavior instrumentation and repeat them for intermittent failures.

## Evidence

- [#109580](../micro_taxo/gh_109580.md): A profiling/trampoline workflow involving process duplication was observed to crash randomly when built with address, memory, or undefined-behavior sanitizers, supporting a sanitizer-sensitive child-process failure in inherited low-level profiling state.

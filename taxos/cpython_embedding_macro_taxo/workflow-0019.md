# Compatibility-guard inversion selects borrowed singleton as owned temporary

A reversed compatibility guard can select a conversion path whose shared-object ownership contract does not match its cleanup logic, causing silent reference-count erosion of a static or cached singleton.

## Precondition

A mispolarized compatibility conditional enables an ownership-sensitive conversion branch on a runtime where a narrowly triggered conversion result is a borrowed reference to a shared singleton.

## Critical operation

The conversion stores that shared singleton in a temporary result that is later handled by generic cleanup.

## Interference

Repeated executions operate on the same process-wide static or cached object, so each erroneous release accumulates against one shared ownership count.

## Invalid assumption

Cleanup assumes the temporary holds an independently owned reference, although the selected conversion path supplied only a borrowed reference.

## Failure

After repeated decrements, later destruction attempts to deallocate the static or cached singleton as heap storage, producing an invalid free and process termination.

## Scope

Singleton cluster: the evidence supports this pattern for compatibility-selected conversion code with mismatched borrowed-versus-owned reference semantics; it does not establish that all conditional branches or all shared-object cleanup failures have this cause.

## Search strategy

1. Audit compatibility and version conditionals that select branches with different reference-ownership contracts; verify their polarity on every supported runtime.
2. Trace ownership of values returned from edge-case conversion branches, especially when they may be interned, cached, or static singletons.
3. Verify that every cleanup release is paired with a proven owned-reference acquisition on all conditional paths.
4. Stress narrowly selected conversion branches in loops and monitor ownership counts of shared results.
5. Inspect shutdown and garbage-collection paths for static or cached objects that could reach ordinary heap deallocation after reference-count corruption.

## Evidence

- [#86863](../micro_taxo/gh_86863.md): A reversed compatibility guard selected a branch that treated a borrowed cached singleton obtained during a subclassed ambiguous-time conversion as an owned temporary; repeated calls decremented its count, and final cleanup attempted to free the static object.

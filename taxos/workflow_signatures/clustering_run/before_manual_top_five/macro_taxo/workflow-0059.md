# Compiler optimization can precede a dependent convergence or legality check, leaving downstream invariants to process transformed or incomplete state

A compiler performs optimization before all checks that depend on the original structure or on fully propagated control flow. In one mechanism, reordered control-flow rewrites leave redundant edges before cleanup converges; in another, optimization removes an invalid context-sensitive construct before its legality check runs. Both expose downstream assertions that assume the relevant state is already normalized and validated.

## Precondition

The compiler input contains either interacting control-flow transformations whose results depend on pass ordering, or a context-sensitive construct located in code eligible for compile-time elimination, while convergence or legality checks are deferred to a later phase.

## Critical operation

Run optimization before completing the dependent control-flow cleanup or validating the construct's contextual legality.

## Interference

Optimization either changes successor relationships after an earlier edge transformation or removes the source construct that would have triggered a recoverable validation error, leaving later compilation with stale control-flow assumptions or metadata derived from the original structure.

## Invalid assumption

A later phase assumes that optimization has reached a fixed point and that all remaining relevant constructs have already passed their contextual validity checks.

## Failure

Compilation reaches an internal assertion or equivalent unrecoverable failure instead of converging successfully or reporting the appropriate source-level error.

## Scope

This is a mixed-cluster umbrella pattern, not a claim that both reports share one narrow implementation mechanism. One report concerns non-converged CFG rewrites and redundant edges; the other concerns optimization bypassing semantic validation of context-sensitive constructs. The shared generalization is that optimization runs ahead of a dependent check whose assumptions are no longer guaranteed.

## Search strategy

1. Trace whether optimization can rewrite control-flow successors after jump threading, edge redirection, or redundant-edge cleanup has already inspected them.
2. Check whether bounded cleanup or invariant checks can run before repeated CFG rewrites reach a fixed point.
3. Find context-sensitive constructs whose legality is checked only after optimization or during code generation.
4. Verify whether dead-code elimination can erase the construct that would have produced a syntax or semantic error while leaving related scope or feature metadata for later phases.
5. Inspect downstream assertions for assumptions that transformed code is both normalized and context-valid without an earlier check that optimization cannot bypass.

## Evidence

- [#114083](../micro_taxo/gh_114083.md): The report shows that constant-dependent branch folding and jump threading in the same phase can observe different successor states; the later fold leaves a redundant jump, and the internal no-redundant-jump check fails until folding is separated and cleanup tracks changes.
- [#121637](../micro_taxo/gh_121637.md): The report shows that optimization can remove invalid asynchronous constructs before deferred context validation, after which later compilation asserts on the presumed-valid scope instead of raising a syntax error; moving validation earlier restores the source-level diagnostic.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0051](../macro_taxo_before_hybrid/workflow-0051.md)
- [workflow-0066](../macro_taxo_before_hybrid/workflow-0066.md)

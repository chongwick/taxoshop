# A control-flow optimizer performs jump threading while constant-dependent branch folding can still rewrite target successors, and bounded cleanup checks invari,

A control-flow optimizer performs jump threading while constant-dependent branch folding can still rewrite target successors, and bounded cleanup checks invariants before reaching a fixed point.

## Precondition

The control-flow graph contains an incoming jump to a block whose leading instructions encode a compile-time constant condition, while jump threading and constant folding are performed in an order that permits both transformations within the same optimization phase.

## Critical operation

The optimizer examines the target's current control flow and attempts to redirect or eliminate the incoming jump before the target's constant condition has been folded into its final unconditional or removed form.

## Interference

Constant folding subsequently changes the target block's successor relationship, invalidating the earlier threading decision and exposing a jump that is now redundant.

## Invalid assumption

The optimizer assumes its bounded cleanup passes have fully propagated the consequences of interacting control-flow rewrites before checking the no-redundant-edge invariant.

## Failure

A redundant jump remains in the graph when the invariant is checked, causing the optimizer's internal assertion to terminate compilation.

## Scope

This is a cautiously scoped pattern from a singleton report: it generalizes to interacting CFG rewrites whose successor changes can invalidate earlier edge transformations, but does not establish that every redundant-edge assertion failure has this cause.

## Search strategy

1. Trace whether constant-condition folding and jump threading inspect or rewrite the same blocks within one pass.
2. Check whether a transformation can change a block's successor after an earlier pass has redirected an incoming edge.
3. Verify that redundant-jump and no-op cleanup repeats until no changes remain rather than using a fixed iteration bound.
4. Inspect invariant checks for control-flow properties that are asserted before all dependent rewrites have reached a fixed point.

## Evidence

- [#114083](../micro_taxo/gh_114083.md): The report shows that constant-dependent branch folding and jump threading in one optimization phase can be ordered so threading observes stale target control flow; the later fold creates a redundant jump, and the fix separates the passes and makes cleanup iterate to convergence.

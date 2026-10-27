# Error-path cleanup of partially acquired state is incomplete or misdirected

Native operations acquire temporary references, builder state, auxiliary allocations, or external-resource state before all fallible work completes. Confirmed cases omit cleanup on exceptional exits; related cases misconfigure cleanup controls, lose the resource through variable shadowing, or rely on a failure sentinel that does not describe partial external state.

## Precondition

An operation owns intermediate state before later input validation, iteration, conversion, callback execution, initialization, resource creation, or multi-input consistency checks have finished.

## Critical operation

The operation continues processing or invokes another fallible stage, then routes failure through an early return, error label, destructor, rollback path, or cleanup helper.

## Interference

The failing path bypasses release, releases only a subset of acquired state, or selects the wrong cleanup behavior through missing initialization, shadowed bindings, inverted conditions, incorrect flag composition, or a callee that may allocate before returning failure.

## Invalid assumption

The implementation assumes every failure reaches complete cleanup and that a null or failure result, cleanup metadata, control flags, or later ownership handoff accurately represents all state acquired so far.

## Failure

Owned direct or indirect allocations remain live after failure, so repeated failing operations accumulate memory and leak detectors report unreclaimed state. Separately, incorrect cleanup state can leave teardown unable to identify the resource or can create stale/double-release risk; those are distinct from the confirmed ownership leaks.

## Scope

The confirmed majority establishes an error-path ownership/cleanup pattern, including the workflow-hypothesized partial multi-input acquisition case. The cluster also contains cleanup-control and binding-state variants, which must not be conflated with use of stale or freed state. Reports 139751, 141044, 142917, and 144069 are weaker boundary evidence: they contain sanitizer leak observations without a confirmed local root cause or fix, and 144069 may be an upstream external-library issue.

## Search strategy

1. Trace every acquired reference, temporary, builder, auxiliary allocation, and external-resource state through validation, iteration, conversion, callback, initialization, and allocation-failure exits; require release or explicit ownership transfer on each path.
2. Inspect multi-input and strict-consistency loops for partially acquired values when exhaustion or another error occurs, and verify that all earlier values are released before returning.
3. Audit cleanup predicates, flag combinations, and conditional branches for inverted release decisions or operators that disable required cleanup.
4. Verify that cleanup-relevant fields are initialized before fallible creation calls and that shared error cleanup sees the original resource binding rather than a shadowed variable.
5. Separate confirmed local ownership leaks from upstream or unconfirmed sanitizer reports, and test repeated failures for retained allocations while checking stale-handle and double-release behavior independently.

## Evidence

- [#139748](../micro_taxo/gh_139748.md): Generated argument-conversion wrappers acquired owned converted values, then later argument conversion failed before the implementation cleanup ran, leaking the acquired value.
- [#139751](../micro_taxo/gh_139751.md): One reproducer reports an allocation leak after invalid input, but the report has no confirmed fix and later includes an unrelated reproducer; it supports only a cautiously bounded failure-path leak observation.
- [#139988](../micro_taxo/gh_139988.md): A builder accumulated owned state and its contents, then an input-addition failure returned without finalizing the builder.
- [#140306](../micro_taxo/gh_140306.md): Several cleanup-control defects caused leaks: a missing error-path free, inverted release logic, and incorrectly combined cleanup flags. These are control-selection variants of the broader cleanup failure, not stale-state evidence.
- [#140398](../micro_taxo/gh_140398.md): Conversion created owned values before an audit hook could fail, and audit-error returns omitted release of those values.
- [#140406](../micro_taxo/gh_140406.md): A method result was owned before type validation, and rejecting the result type returned without releasing it.
- [#140517](../micro_taxo/gh_140517.md): A multi-item iterator path retained already acquired temporary references when strict validation detected exhaustion or another error before processing completed.
- [#140530](../micro_taxo/gh_140530.md): Error construction produced an owned intermediate before a type check failed, and the jump to shared error handling did not release it.
- [#140593](../micro_taxo/gh_140593.md): A parser callback path owned an auxiliary allocation, but a preexisting error took a direct return instead of the common finalization path.
- [#140939](../micro_taxo/gh_140939.md): Formatting acquired a temporary value before buffer growth could fail, and that preparation failure skipped its release.
- [#141044](../micro_taxo/gh_141044.md): The report contains sanitizer-reported direct and indirect leaks after a threading lifecycle sequence, but does not establish the ownership path or a confirmed fix; it is a boundary case rather than proof of the partial-acquisition mechanism.
- [#142917](../micro_taxo/gh_142917.md): A recursion-related sanitizer report was not reproducible and received no confirmed root-cause analysis or fix; it supports only the need to distinguish unconfirmed leak reports from established cleanup defects.
- [#144069](../micro_taxo/gh_144069.md): An external resource-opening call was reported to leak internal allocations when creation failed, while discussion noted that the failure returned no usable handle and that the suspected leak may be upstream; it bounds the pattern around partially initialized external state without proving a local ownership defect.
- [#147998](../micro_taxo/gh_147998.md): A resource binding declared inside a branch shadowed the binding used by shared error cleanup, so the acquired resource became invisible to the cleanup path.
- [#148484](../micro_taxo/gh_148484.md): An iterator was acquired before typecode validation and later initialization steps, and several error returns omitted releasing it; subsequent fixes added cleanup to those exits.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0065](../macro_taxo_before_hybrid/workflow-0065.md)
- [workflow-0089](../macro_taxo_before_hybrid/workflow-0089.md)
- [workflow-0091](../macro_taxo_before_hybrid/workflow-0091.md)
- [workflow-0094](../macro_taxo_before_hybrid/workflow-0094.md)
- [workflow-0144](../macro_taxo_before_hybrid/workflow-0144.md)

# A symbolic optimizer represents predicate results as a distinct value category, but a truthiness-analysis dispatch omits that category; the fallback then readsる

A symbolic optimizer represents predicate results as a distinct value category, but a truthiness-analysis dispatch omits that category; the fallback then reads representation-specific state that is invalid for predicate values, causing a crash instead of returning an unknown or boolean truthiness result.

## Precondition

The optimizer can construct symbolic values for predicate results and later analyze their truthiness through category-based dispatch.

## Critical operation

Dispatch truthiness analysis according to the symbolic value's category.

## Interference

The predicate-result category is missing from the dispatch cases, so processing falls through to logic intended for a different symbolic representation.

## Invalid assumption

Every value reaching the fallback path has the representation fields and invariants expected by that path.

## Failure

Truthiness analysis dereferences invalid state and terminates with a memory-access crash instead of conservatively reporting unknown truthiness or the predicate's known boolean result.

## Scope

This is a cautiously scoped pattern from a singleton report: it applies to category-dispatched symbolic analysis when a newly introduced predicate-result category is omitted, without claiming that all missing dispatch cases fail through the same fallback or produce the same crash.

## Search strategy

1. Enumerate every symbolic-value category and verify that truthiness-analysis dispatch handles each category explicitly.
2. Trace newly added symbolic categories through all category switches, including diagnostic or printing paths.
3. Inspect fallback branches for representation-specific field access and verify their preconditions against every possible category.
4. Add tests covering unknown and constant predicate results before and after truthiness analysis.

## Evidence

- [#144280](../micro_taxo/gh_144280.md): The report shows a distinct symbolic predicate result reaching truthiness analysis, an omitted dispatch case, and a resulting invalid dereference; the fix adds the missing category handling and tests both unknown and constant predicate truthiness.

# Macro Taxonomy: <Pattern Name>

## Pattern

<Describe the recurring bug pattern across multiple micro-taxonomies. Focus on
the shared causal structure: what state is retained or assumed, what operation
invalidates that state or assumption, and how execution reaches the failure.>

## Common Boundary Types

* <Boundary or API category>: <how this pattern appears at this boundary>.
* <Boundary or API category>: <how this pattern appears at this boundary>.
* <Boundary or API category>: <how this pattern appears at this boundary>.
* <Boundary or API category>: <how this pattern appears at this boundary>.

## Failure Shapes

* <Failure mode and the recurring mechanism that produces it>.
* <Failure mode and the recurring mechanism that produces it>.
* <Failure mode and the recurring mechanism that produces it>.
* <Failure mode and the recurring mechanism that produces it>.

## Defensive Rule

<State the general implementation rule that would prevent this family of bugs.
The rule should apply across the representative instances rather than describe
a fix for one specific issue.>

## Representative Micro-taxonomies

* [#XXXXX](../micro_taxo/gh_XXXXX.md): <one-line description of how this issue
  instantiates the pattern>.
* [#XXXXX](../micro_taxo/gh_XXXXX.md): <one-line description of how this issue
  instantiates the pattern>.
* [#XXXXX](../micro_taxo/gh_XXXXX.md): <one-line description of how this issue
  instantiates the pattern>.
* [#XXXXX](../micro_taxo/gh_XXXXX.md): <one-line description of how this issue
  instantiates the pattern>.

## Membership Rule

Group micro-taxonomies whose <reported failure, trigger, vulnerable state,
root cause, or pattern tags> exhibit <the minimal observable conditions that
define membership in this macro taxonomy>.


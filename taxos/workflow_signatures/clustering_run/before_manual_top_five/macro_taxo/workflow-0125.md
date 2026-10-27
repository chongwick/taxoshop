# Availability detection and consumer guards do not match the exact interface entity they expose

Conditional build logic enables a consumer of an optional interface based on a coarse feature marker or a capability probe, while the exact type, member, or declaration is controlled by a narrower condition in the project or target headers. The reports include both guard drift within conditional declarations and probes whose assumptions differ from final compiler target settings.

## Precondition

An optional type, structure member, or function declaration is available only under specific build features, header versions, or target/API settings, while related consumer code is controlled by a separate capability condition.

## Critical operation

A refactor, generated descriptor, or feature-enabled implementation references the optional entity using a broader guard or a configure-time result that was not validated with the exact final headers, target settings, and declaration conditions.

## Interference

The selected build omits the project-defined type, uses external headers without the newer structure member, or suppresses the function declaration for the final target/API level even though the consumer condition remains enabled.

## Invalid assumption

A broad feature macro or successful capability probe is assumed to prove that the specific referenced entity is defined in the compilation unit, although provider and consumer availability conditions are not equivalent.

## Failure

Compilation stops on an undefined type, missing structure member, or undeclared function; dependent metadata or array declarations may then emit cascading diagnostics instead of the unsupported interface being omitted or a fallback being selected.

## Scope

This mixed cluster supports the umbrella rule that availability evidence must match the exact consumer entity and final compilation context. Two reports show conditional-guard drift for project-defined or external structure entities; the third shows a probe-versus-final-target mismatch for a function declaration. They should not be reduced to one specific guard style or to external headers alone.

## Search strategy

1. Trace every optional type, structure-member, and function reference to the exact guard or probe that establishes its availability.
2. Compare consumer guards with the provider's declaration guards, including per-member header conditions rather than only the enclosing feature marker.
3. Verify that configure-time capability checks use the same compiler, target/API settings, headers, and declaration form as the final compilation.
4. Search generated tables, descriptors, shared declarations, and feature-enabled implementations for references protected only by a coarse capability macro.
5. Build with disabled project features, older or minimal external headers, and lower target/API settings to confirm unsupported entities are omitted or replaced by a fallback.

## Evidence

- [#119447](../micro_taxo/gh_119447.md): A refactor made a shared reference to a project-defined runtime state type unconditional while the type remained absent when a numeric build feature disabled its implementation; the failing configuration exposed the guard mismatch.
- [#140159](../micro_taxo/gh_140159.md): A descriptor table was enabled by the availability of a broader platform interface even though a newer member of its structure was absent from supported system headers, producing a missing-member error and incomplete-array follow-on diagnostics.
- [#143640](../micro_taxo/gh_143640.md): A configure-time function check reported success under assumptions that did not match the final target/API-level header conditions, so the guarded call compiled without a declaration and failed under implicit-declaration errors.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0059](../macro_taxo_before_hybrid/workflow-0059.md)
- [workflow-0140](../macro_taxo_before_hybrid/workflow-0140.md)

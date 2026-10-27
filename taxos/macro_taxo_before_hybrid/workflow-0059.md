# Mismatched conditional-availability guards expose an optional type or structure member to a compilation path where its definition is absent.

A compile-time capability is represented by multiple guards, but the guard controlling a consumer is broader or has been removed while the provider remains conditional.

## Precondition

A type or structure member is available only for selected build configurations, feature combinations, or external header versions, with its existence controlled by conditional compilation.

## Critical operation

A refactor or feature addition moves the reference into shared declarations or a metadata table, or otherwise protects it with a capability check that does not exactly match the provider's guard.

## Interference

The build selects a configuration or header set in which the optional entity is omitted even though the consumer-side path is enabled.

## Invalid assumption

The consumer guard or feature macro is assumed to prove that the referenced type or member is defined, although the two availability conditions are not equivalent.

## Failure

Compilation fails on a missing type or structure member; subsequent declarations that depend on the failed initializer may produce secondary incomplete-array or related diagnostics.

## Scope

The reports support this pattern for low-level C code using preprocessor-selected types or platform-header members. They differ in whether the missing entity is project-defined or externally defined, so the general rule is guard alignment rather than any particular platform or feature.

## Search strategy

1. Trace every optional type and structure-member reference to the exact preprocessor guard that defines it.
2. Compare capability macros used at each reference site with the guards controlling the corresponding declaration or header member.
3. Build with configurations that disable each optional feature and with older or minimal platform headers.
4. Search shared declarations, descriptor tables, and generated metadata for entries whose providers are conditionally compiled.
5. Verify that disabled configurations supply either a neutral definition or omit every dependent reference.

## Evidence

- [#119447](../micro_taxo/gh_119447.md): An optional runtime state structure was omitted when a numeric build feature was disabled, but a refactor made its shared-header reference unconditional; the fix supplied a neutral definition for that configuration.
- [#140159](../micro_taxo/gh_140159.md): A descriptor entry was enabled by a feature macro even though the corresponding system-header structure member was absent on some supported header versions, causing a missing-member error and cascading incomplete-array diagnostics.

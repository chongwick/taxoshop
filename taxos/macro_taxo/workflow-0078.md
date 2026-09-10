# A compiler-compatibility configuration symbol is established by multiple detection paths: a capability probe selects a modern annotation spelling, while a later

Independent capability and version checks redundantly define one compiler-configuration symbol when newer toolchains accept both annotation spellings.

## Precondition

A build supports modern and legacy spellings of the same compiler annotation, with capability-based and version-based detection paths targeting one shared configuration symbol.

## Critical operation

The capability probe defines the shared symbol for the modern spelling, while the version fallback independently defines it for the legacy spelling.

## Interference

On newer compilers, both detection predicates are true because the compiler accepts both spellings, so the fallback executes after the symbol has already been defined.

## Invalid assumption

The detection paths are assumed to be mutually exclusive, or the version check is assumed to imply that the shared symbol is still undefined.

## Failure

The compiler reports a duplicate configuration-symbol definition and the build fails; the fallback must be conditional on the symbol not already being defined.

## Scope

This is a singleton cluster, so the pattern is cautiously scoped to compiler-configuration macros or equivalent symbols selected through overlapping capability and version checks.

## Search strategy

1. Inspect compiler capability probes and version fallbacks that define the same configuration symbol.
2. Check whether a version-based fallback is guarded against a symbol established by an earlier feature probe.
3. Trace whether newer toolchains satisfy both detection predicates because they accept both annotation spellings.
4. Verify that alternate compiler spellings are normalized through one guarded definition path.

## Evidence

- [#129838](../micro_taxo/gh_129838.md): The report shows a capability check selecting a modern diagnostic-suppression annotation and an independent compiler-version check selecting a legacy spelling; newer compilers satisfy both, causing a duplicate definition until the fallback is guarded by an undefined-symbol check.

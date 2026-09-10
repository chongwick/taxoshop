# A build-generated configuration header is made less discoverable than external include directories, allowing a stale same-named header to be selected during a “

A source-tree build compiles headers that depend on a generated configuration header, but compiler include-path ordering lets an older externally installed header win. The stale definitions are then combined with current declarations, producing misleading compile-time conflicts.

## Precondition

The build generates a configuration header for the current target, while an older header with the same name remains in a system, sysroot, environment-provided, or dependency-provided include directory.

## Critical operation

Compile source files whose project headers include the configuration header through normal preprocessor search rules.

## Interference

Externally supplied include paths are placed before the project’s generated-header location, or the generated header is stored outside the directory searched relative to the including project header, causing lookup to fall through to the external directory.

## Invalid assumption

The build assumes that a quoted configuration-header include will resolve to the current generated file, or that dependency and environment include flags cannot override the project configuration.

## Failure

The compiler consumes stale configuration macros alongside current source declarations, causing macro redefinitions, incompatible types, or other compile errors instead of clearly identifying the wrong-header selection.

## Scope

This is a singleton cluster, so the pattern is scoped to generated configuration headers with duplicate external installations and vulnerable include-path or header-placement rules; it does not claim that all stale-header failures arise from the same build-system design.

## Search strategy

1. Trace every generated configuration header from its generation path to each compiler include path and verify that the current file is searched first.
2. Inspect how dependency, sysroot, environment, and user-supplied include flags are ordered relative to project and build directories.
3. Check quoted and angled includes of same-named generated headers for fallback paths that can reach system installations.
4. Compile with a deliberately stale same-named external header and verify that the build either ignores it or emits an explicit header-selection diagnostic.

## Evidence

- [#129019](../micro_taxo/gh_129019.md): The report shows a source build selecting an older system-installed configuration header because compiler flags and header placement allowed external lookup to precede the generated file; removing the stale header or placing the generated header in the project include directory resolved the conflicting macros and types.

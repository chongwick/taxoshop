# Unsupported target accepted for optional code generation until artifact generation fails

An optional target-specific generator is enabled for an unsupported target; configuration accepts it, generation rejects the target without producing the required artifact, and dependent compilation fails later.

## Precondition

An optional generated-artifact feature is enabled while the selected target is outside the generator’s supported target set.

## Critical operation

The build invokes the generator and then compiles source files that depend on its output.

## Interference

Configuration does not validate target support, and generator rejection leaves the required artifact unavailable to downstream compilation.

## Invalid assumption

Successful configuration is treated as evidence that generation will succeed and provide the required artifact for the selected target.

## Failure

The build fails late with an unsupported-target generator error or a missing generated-artifact compilation error instead of rejecting the unsupported configuration early.

## Scope

This is a singleton cluster, so the pattern is scoped to optional target-specific code generation whose unsupported-target validation is missing or delayed until artifact generation.

## Search strategy

1. Check optional code-generation configuration paths for validation against the generator’s supported-target registry.
2. Trace generator rejection paths and verify that unsupported targets stop the build with an explicit diagnostic before dependent compilation.
3. Check build dependencies to ensure consumers cannot compile when required generation fails or emits no artifact.
4. Search for target identifiers accepted by configuration but absent from the generator’s recognized-target set.

## Evidence

- [#140354](../micro_taxo/gh_140354.md): The report shows an optional code-generation feature accepted for an Android target absent from the generator’s known targets; generation rejects the target, the generated header is not produced, and compilation subsequently fails because the header is missing.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0097](../macro_taxo_before_hybrid/workflow-0097.md)

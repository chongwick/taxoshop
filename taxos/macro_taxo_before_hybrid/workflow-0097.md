# An optional target-specific code-generation feature is enabled for a target outside the generator’s supported target set, but configuration accepts it without a

A target-specific generator is enabled for an unsupported target; configuration accepts the setting, generation rejects the target without producing the required artifact, and the build surfaces either the generator error or a downstream missing-artifact compilation error.

## Precondition

An optional generated-artifact feature is enabled while the selected target is not recognized as supported by its generator.

## Critical operation

The build invokes the generator and compiles source files that depend on the generated artifact.

## Interference

Target support is not validated during configuration, and generator rejection does not produce the artifact required by dependent compilation.

## Invalid assumption

Successful feature configuration is treated as evidence that generation will succeed and provide the artifact for the selected target.

## Failure

The build fails late with an unsupported-target generator diagnostic or a missing generated-artifact compilation error instead of rejecting the configuration early.

## Scope

This is a singleton cluster, so the pattern is scoped to target-specific optional code generation where unsupported-target validation is missing or delayed until artifact generation.

## Search strategy

1. Check optional code-generation configuration paths for validation against the generator’s supported-target set.
2. Trace generator rejection paths and verify that unsupported targets produce an explicit configuration-time or build-stopping diagnostic.
3. Check build dependencies to ensure consumers cannot compile when required generation fails or emits no artifact.
4. Search for target identifiers accepted by configuration but absent from the generator’s recognized-target registry.

## Evidence

- [#140354](../micro_taxo/gh_140354.md): The report shows an optional JIT-related generator being enabled for an Android target that is absent from the generator’s known targets; configuration succeeds, generation rejects the target, and the required generated header is then unavailable to compilation.

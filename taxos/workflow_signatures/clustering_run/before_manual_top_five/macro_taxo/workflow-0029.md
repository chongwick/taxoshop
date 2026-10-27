# Generated configuration scripts trust unvalidated external tool commands or dialects.

Configuration generation embeds external-tool commands or edit syntax into shell scripts without ensuring that the selected tool is available and semantically compatible in the target environment.

## Precondition

The generator relies on host utilities or interpreters whose names, availability, or command dialects vary across supported environments.

## Critical operation

It probes or selects a tool and embeds its invocation or multiline transformation commands into generated configuration or build scripts.

## Interference

A missing, differently named, or dialect-incompatible tool leaves an unresolved command or raw edit fragment in the generated script.

## Invalid assumption

A nominal tool match or successful probe is assumed to guarantee exact command availability and portable execution semantics.

## Failure

The shell executes leaked transformation text or cannot resolve the selected command, so configuration or subsequent build generation aborts with a misleading script error.

## Scope

The common pattern is unvalidated external-tool dependence in generated configuration workflows. The reports include both dialect-sensitive text transformation and unavailable host-command selection; they should be reviewed as related mechanisms, not as one specific utility failure.

## Search strategy

1. Trace every detected external tool or interpreter into generated scripts and verify the exact command is executable at its use site.
2. Inspect generated multiline editing commands for syntax differences across all supported utility implementations.
3. Test configuration with missing, versioned, and alternate-dialect host tools and inspect the generated script before execution.
4. Add explicit validation and diagnostics when a selected host tool is unavailable or cannot perform the required transformation.

## Evidence

- [#94404](../micro_taxo/gh_94404.md): A generated configuration edit used multiline insertion syntax accepted by one text-processing dialect but rejected by another, causing configuration to fail on a supported platform.
- [#98249](../micro_taxo/gh_98249.md): Cross-build configuration embedded an unversioned host interpreter command after an inadequate selection path; the later generation rule failed because that exact command was unavailable.
- [#116259](../micro_taxo/gh_116259.md): Configuration emitted a raw edit fragment into its shell script, where the shell treated it as a command and then reported a syntax error; related discussion points to an unmet external-tool requirement.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0028](../macro_taxo_before_hybrid/workflow-0028.md)
- [workflow-0031](../macro_taxo_before_hybrid/workflow-0031.md)

# In cross-compilation, host-side build tooling is selected by name without validating that the exact command is executable and suitable in the build environment;

A cross-build configuration records an interpreter command for host-side generation, but the selected command does not actually resolve in the build environment.

## Precondition

Cross-compilation requires a host-executed interpreter for generating build-time artifacts, while the environment may provide only a differently named or versioned interpreter.

## Critical operation

Configuration probes for and embeds an interpreter command into generated build rules without validating that the exact selected command is available and runnable.

## Interference

The generated rules invoke the recorded command during host-side artifact generation, but command-name or version mismatches make that invocation unavailable.

## Invalid assumption

A discovered or selected command name is assumed to identify an executable compatible with the build environment, without checking exact availability and suitability.

## Failure

The shell cannot resolve the embedded interpreter when generation begins, so the generation target fails and the overall cross-build terminates.

## Scope

This is a cautiously scoped singleton pattern: it generalizes the demonstrated cross-compilation failure in which host-tool command selection is not validated, without asserting that every interpreter-selection failure has the same cause.

## Search strategy

1. Inspect cross-compilation configuration probes for interpreter names that are recorded without an exact executable or usability check.
2. Trace every configured host-tool variable into generated build rules and verify that the invoked command is resolvable on the build host.
3. Check fallback selection paths for unversioned commands when only versioned interpreters are installed.
4. Add a configuration-time validation or clear diagnostic for missing or incompatible host-side generators.

## Evidence

- [#98249](../micro_taxo/gh_98249.md): The report shows a cross-build selecting an unversioned interpreter command, embedding it in generated rules, and failing when the shell cannot find that command; it also documents that differently named or versioned installed interpreters did not match the selected command.

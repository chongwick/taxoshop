# Cross-build configuration can embed an unavailable or version-incompatible host interpreter command into generated rules for host-side generation.

Validate configured host-side tool commands, including required version compatibility, before propagating them into generated build rules.

## Precondition

A cross-build requires a host-side interpreter for generation, while the host lacks the matching versioned interpreter and may provide only a differently versioned command.

## Critical operation

Configuration records a host-interpreter command and emits it into build rules used for host-side generation.

## Interference

The generated rule invokes an unversioned interpreter command that the build shell cannot locate.

## Invalid assumption

A command selected or recorded during configuration is both executable in the build environment and suitable for the required interpreter version.

## Failure

The host-side generation step fails with an executable-not-found error, terminating the build.

## Scope

Singleton cluster: this pattern is limited to configuration-generated host-interpreter commands used during cross-build generation; the report does not establish behavior for other build tools or fallback mechanisms.

## Search strategy

1. Check every configured host-side tool command with an executable lookup before writing it into generated build rules.
2. Check that a host interpreter selected for cross-build generation has the required version, not merely a compatible command name.
3. Trace generated host-side generation rules to ensure they invoke the validated configured tool rather than a fallback command.
4. Fail configuration with a clear diagnostic when no suitable host-side interpreter is available.

## Evidence

- [#98249](../micro_taxo/gh_98249.md): A cross-build generated a host-side generation rule using an unversioned interpreter command; the shell could not find it, and the report identified absence of the required matching host interpreter version as the relevant environment constraint.

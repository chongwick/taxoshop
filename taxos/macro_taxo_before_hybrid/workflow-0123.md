# A compiler/toolchain configuration combined with experimental runtime code generation and undefined-behavior instrumentation can leave a lazily dispatched JIT/g

A compiler/toolchain configuration combined with experimental runtime code generation and undefined-behavior instrumentation can leave a lazily dispatched generated-code target unusable during bootstrap execution.

## Precondition

The build enables experimental runtime code generation and undefined-behavior instrumentation, using an affected compiler/toolchain configuration.

## Critical operation

A bootstrap executable reaches the runtime's lazy generated-code dispatch trampoline while performing ordinary initialization or code-generation work.

## Interference

The lazy dispatch target contains an invalid or otherwise unusable generated-code address under that compiler and instrumentation combination.

## Invalid assumption

The trampoline assumes the generated-code address is valid and dereferenceable when dispatch begins, without establishing a safe fallback before reading through it.

## Failure

The instrumented read through the unusable address raises a segmentation fault and aborts the bootstrap build instead of completing code generation.

## Scope

This is a cautiously scoped singleton pattern. The report supports the interaction between an affected compiler/toolchain, instrumentation, experimental generated-code dispatch, and bootstrap execution; it does not establish the underlying reason the generated address becomes invalid or a broader rule for all compilers, sanitizers, or JIT implementations.

## Search strategy

1. Inspect lazy code-generation trampolines for unchecked reads or calls through generated-code addresses.
2. Trace every initialization and publication path for generated-code targets under compiler and sanitizer builds.
3. Compare generated-code address setup and dispatch behavior across supported compilers when experimental code generation and undefined-behavior instrumentation are enabled.
4. Check whether bootstrap execution can reach lazy dispatch before the generated target is validated, materialized, or given a fallback implementation.

## Evidence

- [#141621](../micro_taxo/gh_141621.md): The report documents a singleton failure in which experimental runtime code generation plus undefined-behavior instrumentation crashes a bootstrap executable under several Clang versions, with the sanitizer stack identifying a lazy generated-code trampoline performing the invalid read; the same configuration succeeds with the default compiler, so a

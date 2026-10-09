# Target-specific LTO code generation exceeds a branch encoding range

An LTO-enabled build on a target architecture produces assembly whose branch displacement cannot be encoded, causing the toolchain to reject an intermediate executable.

## Precondition

A build enables link-time optimization on a target/toolchain combination that encounters a branch-range limitation.

## Critical operation

The toolchain performs LTO code generation while linking an intermediate executable.

## Interference

Generated assembly contains a branch whose target is outside the encodable range.

## Invalid assumption

The build assumes the target toolchain can complete LTO code generation for this executable without violating branch-encoding constraints.

## Failure

The assembler rejects the out-of-range branch; the LTO wrapper and linker then fail, aborting the build.

## Scope

Singleton cluster. The report supports an LTO-dependent, target-toolchain branch-range failure, but does not establish a particular optimization pass, layout algorithm, or source-code cause.

## Search strategy

1. Check whether link-time optimization is enabled for targets with known branch-range or code-layout limitations.
2. Rebuild the failing link without link-time optimization to isolate toolchain-generated code from source-level failures.
3. Inspect LTO-generated assembly and assembler diagnostics for out-of-range branch instructions.
4. Verify that the compiler, assembler, and linker versions support LTO on the affected target architecture.
5. Add a target-specific build probe for successful LTO linking of a representative large intermediate executable.

## Evidence

- [#93619](../micro_taxo/gh_93619.md): An LTO-enabled build on a 64-bit target fails while linking an intermediate executable because the assembler reports a branch out of range; removing LTO makes the build succeed.

# Large whole-program link-time optimization on an architecture with limited branch displacement is applied to a sufficiently large codebase.

Global optimization and code generation create a final layout in which a direct branch target is farther away than the target architecture's instruction encoding permits.

## Precondition

A large build enables link-time or whole-program optimization on a target architecture with range-limited direct branches.

## Critical operation

The link-time compiler combines, optimizes, and lays out code before emitting machine instructions for an intermediate executable.

## Interference

Global code placement and expansion increase the distance between a branch instruction and its target beyond the encodable displacement.

## Invalid assumption

The code-generation pipeline assumes each emitted direct branch will remain in range, or that the assembler/linker will automatically provide a long-branch alternative or relaxation.

## Failure

The assembler rejects the generated instruction with an out-of-range branch diagnostic, causing link-time compilation and the build of the intermediate executable to abort; disabling link-time optimization avoids the failure path.

## Scope

This is a singleton report, so the pattern is scoped to toolchain failures where whole-program code placement exposes an architecture-specific branch-range limit; it does not establish that all link-time optimization failures or all out-of-range branches have this cause.

## Search strategy

1. Search architecture-specific branch emission and relaxation logic for direct branches that lack a long-range fallback after whole-program layout.
2. Check code-generation assumptions that branch targets remain within encoding range after global optimization, partitioning, or section reordering.
3. Inspect linker and assembler support for relaxing or rewriting out-of-range branches in link-time-generated code.
4. Exercise large link-time-optimized builds on architectures with limited branch reach, comparing the same build with link-time optimization disabled.

## Evidence

- [#93619](../micro_taxo/gh_93619.md): A large optimized build on a range-limited architecture failed during link-time compilation because the assembler reported an out-of-range branch; the same build succeeded when link-time optimization was removed.

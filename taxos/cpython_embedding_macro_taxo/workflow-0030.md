# Instrumented initialization trips an allocator range check on a wild pointer

A memory-instrumented build aborts during early runtime initialization when cleanup of resized internal storage routes a pointer through an allocator address-range classifier that reads invalid heap memory.

## Precondition

A runtime using an allocator-specific deallocation path is built and run with heap-access instrumentation enabled.

## Critical operation

Early initialization grows an internal mapping and releases its replaced storage through the generic object deallocation path.

## Interference

The allocator's address-range classification performs a read at a wild, instrumenter-protected address.

## Invalid assumption

The deallocation path assumes that it can safely inspect or range-classify the supplied pointer before establishing that the accessed memory is valid in the current allocation environment.

## Failure

Heap instrumentation reports a heap-buffer-overflow and aborts the initialization helper, causing its enclosing build command to fail.

## Scope

Cautiously scoped singleton pattern. The report demonstrates the failing deallocation/range-check sequence under address instrumentation, but does not establish a confirmed root fix, broad allocator incompatibility, or reproduction on other versions or platforms.

## Search strategy

1. Audit deallocation paths for ownership or address-range classifiers that dereference or inspect an incoming pointer before validating it.
2. Trace storage released by container-resize cleanup to confirm that allocation and deallocation routes use compatible allocator domains.
3. Exercise early runtime initialization under heap-access instrumentation, including helper executables invoked by the build.
4. Review allocator fast paths for assumptions about pointer layout, provenance, or readable surrounding metadata under instrumented heaps.

## Evidence

- [#96714](../micro_taxo/gh_96714.md): An instrumented build aborts during early initialization: internal mapping growth releases prior storage, the object deallocator calls an allocator address-range check, and that check produces a heap-buffer-overflow on a wild pointer; the aborted helper then fails the build command.

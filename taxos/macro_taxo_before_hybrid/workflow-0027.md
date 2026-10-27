# Forked child inherits live process/thread state that ordinary shutdown cannot reclaim under leak detection

A fork-like child is created from a multithreaded or otherwise initialized process, and inherited state belonging to threads that do not survive in the child remains unreclaimed until child termination.

## Precondition

The parent has live process-wide bookkeeping or thread-associated allocations, and a child is created while leak detection is enabled.

## Critical operation

The child continues through the program's ordinary shutdown or interpreter-exit path after duplicating the parent's address space.

## Interference

Only the creating thread survives the fork, while allocations and bookkeeping associated with other threads or inherited global runtime state remain present in the child without the owners or cleanup activity that would normally release them.

## Invalid assumption

Forking produces a child whose ordinary shutdown can reclaim all inherited runtime state as though it had been initialized independently or all original threads still existed.

## Failure

Leak detection reports residual allocations at child exit, converts the child termination into a nonzero status, and causes a parent wait or supervising workflow that expects success to fail.

## Scope

This pattern is limited to fork-like address-space duplication in a process with live threaded or process-wide runtime state and fatal child-exit leak checking. The first report also includes independent leaks from ordinary shutdown and deliberate retained allocations, which are outside this pattern.

## Search strategy

1. Check fork-like child creation sites for execution while worker threads or thread-owned runtime allocations may still be live.
2. Check the child branch for ordinary high-level shutdown instead of an immediate, fork-safe successful termination path.
3. Check whether inherited process-wide registries, thread stacks, locks, sentinels, or allocator bookkeeping have explicit child-side reset or cleanup handling.
4. Check sanitizer and leak-detector configuration to see whether child-exit leaks are fatal and whether the parent asserts a zero child status.

## Evidence

- [#94064](../micro_taxo/gh_94064.md): The report shows forked child tests failing because leak detection found inherited runtime and thread-related allocations at shutdown; the child exited with status 1 where the parent expected status 0. The same report also contains unrelated shutdown-only and deliberate leaks, so only its forked-child evidence supports this pattern.
- [#140493](../micro_taxo/gh_140493.md): The report creates a child while multiple threads are active and records leak-detector findings; its accompanying analysis explains that the non-calling threads disappear while their stacks and associated allocations remain in the child, establishing the fork-plus-live-thread mechanism.

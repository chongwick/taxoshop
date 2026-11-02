# Heterogeneous numeric equality comparisons can expose an intermittent platform-sensitive memory-safety defect.

A mixed-representation comparison path is unsafe on some 32-bit environments and may crash nondeterministically.

## Precondition

A runtime compares numerically related values represented by multiple numeric implementations, including at least one implementation with low-level native behavior, on affected 32-bit platforms.

## Critical operation

Execute repeated equality comparisons across those heterogeneous representations.

## Interference

Operand-type-dependent comparison dispatch and platform-specific low-level behavior alter the path taken, with failures observed on multiple 32-bit architectures but not consistently elsewhere.

## Invalid assumption

The comparison machinery is assumed to handle every supported representation combination with memory-safe, deterministic behavior regardless of operand order or platform.

## Failure

An intermittent invalid memory access terminates the process with a segmentation fault; rerunning the same workload may succeed.

## Scope

This is a cautiously scoped singleton pattern. The evidence supports a platform-sensitive defect in heterogeneous numeric comparison, but does not prove whether the underlying fault is a particular implementation, compiler, allocator, or memory-corruption mechanism.

## Search strategy

1. Audit equality-comparison dispatch for every supported pair of numeric representations.
2. Trace mixed-type comparison paths that cross native implementation boundaries or use platform-width-sensitive data.
3. Check whether operand order selects different conversion, coercion, or comparison routines.
4. Run the same heterogeneous comparison matrix repeatedly on 32-bit targets under memory-safety instrumentation.

## Evidence

- [#77808](../micro_taxo/gh_77808.md): The report documents intermittent process-segmentation faults while comparing values drawn from several numeric representations, with the crash reproduced on 32-bit x86 and ARM environments and sometimes absent on rerun; it localizes the failure to a mixed equality-comparison workload but does not establish a more specific root cause.

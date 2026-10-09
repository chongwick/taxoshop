# Intermittent crash during repeated cross-representation equality comparison on 32-bit builds

A runtime repeatedly performs equality checks in both operand orders between a complex-valued representation and several other numeric representations; on affected 32-bit builds, the comparison path can fault nondeterministically.

## Precondition

A workload iterates over multiple numeric representations and compares each with a complex-valued value in both operand orders.

## Critical operation

Dispatch and execute cross-representation equality comparison for each operand pair.

## Interference

The workload runs on affected 32-bit Linux environments, where the same test can intermittently fail and then pass when rerun.

## Invalid assumption

The comparison implementation assumes every selected cross-representation equality path is safe and repeatable under the affected 32-bit execution environment.

## Failure

An invalid native-memory access causes a segmentation fault and terminates the process.

## Scope

Singleton cluster. The evidence supports an intermittent 32-bit mixed-comparison crash pattern, but does not identify the specific representation pair, native mechanism, or a confirmed root cause.

## Search strategy

1. Inspect bidirectional mixed-type equality dispatch for representation pairs that can reach different implementation paths.
2. Check native comparison implementations for pointer, reference, and temporary-object lifetime assumptions that differ on 32-bit targets.
3. Exercise repeated mixed-representation equality comparisons on supported 32-bit architectures and record intermittent faults.
4. Audit comparison error and fallback paths to ensure they cannot leave invalid state for a subsequent comparison.

## Evidence

- [#77808](../micro_taxo/gh_77808.md): A loop comparing a complex-valued value with several numeric representations in both orders intermittently segfaulted on multiple 32-bit Linux builders; rerunning the same test could pass. The report identifies no confirmed root cause or sanitizer diagnosis.

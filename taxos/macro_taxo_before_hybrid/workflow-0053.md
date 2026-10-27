# Unchecked numeric input reaches native code that assumes a valid handle or range, causing unsafe memory access.

A caller-controlled integer is accepted by an interface and forwarded to native code without validating its semantic domain; the native routine then uses it as a trusted handle or bounded value, potentially accessing invalid memory and terminating the process instead of returning an input error.

## Precondition

A caller supplies a numeric value outside the valid identifier or range domain, while the interface performs only syntactic conversion or type checking.

## Critical operation

The interface forwards the converted value to a native routine without validating that it denotes a live resource or falls within the supported range.

## Interference

The native routine interprets the value as a trusted internal handle, pointer-like value, count, or boundary and uses it in memory-access operations.

## Invalid assumption

A successfully converted numeric argument is semantically valid for the native operation.

## Failure

The invalid value can cause an out-of-bounds or invalid-memory access, terminating the process instead of producing a recoverable argument error.

## Scope

The reports support a general pattern of missing semantic validation at a native-interface boundary. They differ in whether the value is used as a thread handle or a count, so the pattern does not claim that all invalid numeric arguments cause the same specific memory fault.

## Search strategy

1. Check numeric arguments passed to native routines for semantic range, sign, liveness, and representability validation before forwarding.
2. Check whether native code uses caller-controlled integers as handles, pointer-like values, counts, indexes, or memory boundaries without defensive validation.
3. Check invalid, negative, extreme, stale, and out-of-range inputs for recoverable errors rather than crashes or sanitizer-detected memory faults.
4. Check interface conversion code for type checks that are mistaken for validation of the value’s operational domain.

## Evidence

- [#115378](../micro_taxo/gh_115378.md): An invalid numeric thread identifier is converted and passed to native lookup code, which treats it as a pointer-like thread handle and dereferences it, producing a segmentation fault.
- [#122431](../micro_taxo/gh_122431.md): A negative numeric count, including an extreme minimum value, reaches native history-processing code without rejection and can cause an out-of-bounds memory access; the fix adds explicit range validation and a recoverable value error.

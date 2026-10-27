# Unchecked numeric values cross native boundaries without semantic or size validation

An interface accepts a numerically representable value without validating its semantic validity or the downstream component’s effective limits. Native code then treats the value as a live handle, valid count, or safe geometry parameter, allowing invalid memory access or arithmetic corruption instead of a recoverable argument error.

## Precondition

A caller supplies an invalid identifier or count, or an extreme coordinate or dimension that is representable at the interface but invalid or unsupported by downstream native code.

## Critical operation

The interface forwards the converted value to a native routine without checking liveness, sign, semantic range, representability, or the callee’s effective geometry limits.

## Interference

The downstream routine interprets the value as a pointer-like handle and dereferences it, uses an invalid count in indexing or memory arithmetic, or uses extreme geometry in narrower conversions and internal layout or address calculations.

## Invalid assumption

Successful type conversion or surface-level representability is assumed to prove that the value is semantically valid and safe for the downstream implementation to process.

## Failure

The dependency may dereference an invalid address, access memory out of bounds, or corrupt internal arithmetic state, terminating the process instead of returning a controlled value, range, or bounds error.

## Scope

This is a hybrid umbrella pattern covering two related but distinct native-boundary failures: invalid identifiers or counts reaching code that assumes semantic validity, and extreme geometry reaching a dependency whose internal representation or arithmetic cannot safely handle it. The reports do not establish one universal downstream fault or that every case can be prevented solely by changing the wrapper; they support checking both interface validation and dependency behavior.

## Search strategy

1. Check native-boundary identifiers and pointer-like numeric arguments for liveness and semantic validation before forwarding them.
2. Check counts, lengths, and offsets for sign, minimum-value, overflow, and indexing validation before native memory operations.
3. Check geometry wrappers for explicit validation against the downstream component’s actual coordinate and dimension limits, including narrower internal types.
4. Trace extreme numeric inputs through native conversions and arithmetic to verify that invalid addresses, overflow, and out-of-bounds access become recoverable errors.
5. Check that type conversion and integer representability are not being treated as evidence of operational validity or safe dependency behavior.

## Evidence

- [#115378](../micro_taxo/gh_115378.md): A caller-controlled thread identifier is converted successfully and passed to native lookup code, which casts it to a pointer-like internal handle and dereferences it without validating that it denotes a valid thread, causing a segmentation fault.
- [#120378](../micro_taxo/gh_120378.md): Large resize dimensions were accepted as ordinary integers even though the lower-level terminal implementation used narrower dimensions; the resulting overflow corrupted internal state and later screen activity crashed, so the interface was changed to reject values outside the narrower range.
- [#122431](../micro_taxo/gh_122431.md): Negative and minimum signed count values reached native history-processing code without semantic validation; the dependency used them in memory-related processing and could access out-of-bounds memory, so negative values were changed to produce a recoverable value error.
- [#140462](../micro_taxo/gh_140462.md): An extreme window coordinate was forwarded unchanged to a lower-level geometry implementation that failed to reject it before internal processing; the resulting invalid address computation caused a segmentation fault rather than a bounds error.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0053](../macro_taxo_before_hybrid/workflow-0053.md)
- [workflow-0061](../macro_taxo_before_hybrid/workflow-0061.md)

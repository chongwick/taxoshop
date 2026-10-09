# Allocator alignment below the platform ABI requirement for general object storage

A general-purpose allocator guarantees less alignment than the platform ABI requires for allocated objects, allowing ordinarily used object storage to be misaligned.

## Precondition

On a platform whose ABI requires a stricter allocation alignment, an allocator partitions or returns blocks using a smaller alignment boundary.

## Critical operation

The runtime allocates and uses general object storage from those blocks.

## Interference

Compiler-generated code increasingly relies on the platform-required alignment when accessing allocated objects.

## Invalid assumption

The allocator assumes its smaller alignment guarantee is sufficient for general object storage despite the stricter ABI requirement.

## Failure

Misaligned object storage violates the platform alignment contract and causes undefined behavior during normal execution.

## Scope

Singleton cluster: this pattern is limited to a general-purpose allocator whose alignment guarantee is below the applicable ABI requirement; the report does not establish behavior for deliberately over-aligned object types beyond that baseline contract.

## Search strategy

1. Check every general-purpose allocator's returned-block alignment against the applicable platform ABI.
2. Trace size-class, pool, and arena stride calculations to verify that each preserves the required allocation alignment.
3. Audit custom allocation fast paths separately from system-allocation fallbacks for weaker alignment guarantees.
4. Compile and run allocation-heavy paths with alignment undefined-behavior diagnostics enabled on each supported word size.

## Evidence

- [#72174](../micro_taxo/gh_72174.md): A runtime allocator returned blocks aligned to a smaller boundary than the 64-bit ABI-required alignment; increasing the allocator's alignment was required to conform to the ABI and avoid undefined behavior as compilers relied on that guarantee.

# Optimized diagnostic code uses a representation incompatible with the metadata table's indexing domain, causing an unchecked table lookup to read beyond the end

A diagnostic path indexes fixed metadata with a transformed instruction identifier whose value space differs from the table's canonical index space.

## Precondition

A system maintains fixed-size metadata indexed by canonical instruction or operation identifiers, while an optimization or lowering stage can rewrite those identifiers into another representation.

## Critical operation

Diagnostic formatting directly uses the transformed identifier as an index into the canonical metadata table.

## Interference

The optimization/lowering transformation changes the identifier's numeric value or domain without restoring the canonical index before diagnostics run.

## Invalid assumption

The formatter assumes every instruction identifier it receives is a valid in-bounds index for the metadata table.

## Failure

Ordinary diagnostic output performs an out-of-bounds read from the metadata table, which memory-safety instrumentation may report as a global buffer over-read and terminate the process.

## Scope

This is a singleton cluster, so the pattern is scoped to diagnostic metadata lookups over transformed instruction representations; it does not establish that all optimizer-induced table over-reads share this exact representation mismatch.

## Search strategy

1. Trace every identifier used to index diagnostic metadata back through optimization and lowering transformations.
2. Check that transformed operation codes are converted back to the metadata table's canonical index space before lookup.
3. Verify that fixed-table lookups validate both the identifier domain and numeric bounds at diagnostic call sites.
4. Compare the declared metadata-table range with all values producible by optimized or lowered instructions.
5. Exercise diagnostic and tracing paths under optimized representations with bounds instrumentation enabled.

## Evidence

- [#142629](../micro_taxo/gh_142629.md): The report demonstrates that an optimized instruction carried a transformed opcode representation, while the diagnostic formatter indexed a fixed metadata-flags table with that value; the mismatch produced an instrumented global out-of-bounds read during normal trace printing, and the fix mapped the opcode back to its uncached canonical index.

# An instrumented runtime’s custom allocator probes ownership metadata for a pointer during early initialization, but the instrumentation changes the pointer’s or

An instrumented runtime’s custom allocator probes ownership metadata for a pointer during early initialization, but the instrumentation changes the pointer’s or allocation’s layout so the probe reads beyond valid heap storage.

## Precondition

A runtime uses a custom allocator that classifies pointers by reading allocator-specific address or in-band metadata, and memory-error instrumentation is enabled across the runtime.

## Critical operation

Early initialization resizes an internal mapping or container and releases its previous storage through the custom deallocation path.

## Interference

Instrumentation changes allocation routing or layout, including redzones and metadata placement, so the released pointer does not conform to the custom allocator’s expected representation.

## Invalid assumption

The deallocator assumes every pointer reaching its classification routine belongs to the allocator’s own metadata domain and can be inspected using its normal ownership test.

## Failure

The ownership test reads outside valid heap storage; the instrumentation reports a heap-buffer-overflow and aborts the helper, causing the surrounding build or initialization command to fail.

## Scope

This is a singleton cluster. It supports the interaction between whole-runtime memory instrumentation and allocator metadata probing during initialization; it does not establish that all custom allocators or all instrumentation configurations fail, nor that the downstream build command is itself the defect.

## Search strategy

1. Trace every custom deallocation ownership check and verify that its metadata reads are valid for pointers allocated under the active instrumentation runtime.
2. Inspect early initialization paths for container growth or mapping replacement that frees storage before allocator and instrumentation compatibility has been established.
3. Compare allocation and deallocation domains across instrumented and non-instrumented builds, including redzones, headers, and pointer-classification assumptions.
4. Add an instrumented test that exercises the first initialization-time resize and confirms that foreign or differently laid-out pointers are rejected without dereferencing invalid metadata.

## Evidence

- [#96714](../micro_taxo/gh_96714.md): The report shows address instrumentation enabled for the runtime, an initialization-time mapping resize, deallocation through a custom small-object allocator, an ownership probe reading a wild pointer outside valid heap storage, instrumentation aborting the helper, and the build failing on the resulting command exit.

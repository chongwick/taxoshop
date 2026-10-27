# Instrumented allocation crosses a custom allocator’s ownership-probe boundary.

A memory-instrumented runtime frees storage through a custom allocator whose ownership probe cannot safely classify the instrumented pointer, causing an invalid metadata read during early initialization.

## Precondition

A runtime combines whole-program memory instrumentation with a custom allocator that classifies freed pointers by inspecting allocator-specific address or metadata state.

## Critical operation

Early initialization grows an internal mapping or container and releases its previous storage through the custom deallocation path.

## Interference

Instrumentation changes the allocation environment or pointer layout, so the released pointer does not satisfy the custom allocator’s assumptions for safe ownership classification.

## Invalid assumption

The deallocator assumes every pointer reaching its classification routine belongs to its own metadata domain and can be probed before being redirected or rejected.

## Failure

The ownership probe reads outside valid heap storage; instrumentation reports a heap-buffer-overflow and aborts the helper, causing the surrounding build command to fail.

## Scope

This singleton supports an initialization-time interaction between memory instrumentation and custom allocator ownership probing. It does not establish that every allocator or instrumentation configuration is incompatible, nor that the downstream build command is the underlying defect.

## Search strategy

1. Trace custom deallocation ownership probes and verify that every metadata read is valid for instrumented and non-instrumented pointers.
2. Inspect early initialization for container growth that frees storage before allocator and instrumentation compatibility is established.
3. Compare allocation and deallocation domains, including pointer-layout and ownership-classification assumptions, across instrumented builds.
4. Exercise the first initialization-time resize under instrumentation and verify that foreign pointers are rejected without dereferencing invalid metadata.

## Evidence

- [#96714](../micro_taxo/gh_96714.md): The report shows address instrumentation enabled across the runtime, an initialization-time mapping resize, custom deallocation, an ownership probe reading a wild pointer outside valid heap storage, instrumentation aborting the helper, and the build failing on that command.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0030](../macro_taxo_before_hybrid/workflow-0030.md)

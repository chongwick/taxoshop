# Shared-memory aggregate initialization performs an unchecked bulk serialization write through an unusable destination, causing a native memory fault.

A shared-memory-backed aggregate is initialized by serializing ordinary values directly into its backing storage. If the write destination is invalid or unusable, the native bulk write faults instead of producing a recoverable initialization error.

## Precondition

A shared-memory-backed aggregate is being initialized and its values must be serialized into backing storage.

## Critical operation

Initialization performs a native bulk write of the serialized representation into the backing-storage destination.

## Interference

The destination address is invalid or does not refer to usable writable backing storage when the bulk write occurs; this report does not establish why that state arises.

## Invalid assumption

The initialization path assumes the destination remains valid and writable without validating it immediately before the bulk write.

## Failure

The bulk write dereferences the unusable destination, producing a memory-safety fault and aborting the process rather than returning a recoverable initialization failure.

## Scope

This is a singleton report, so the pattern is limited to the observed shared-memory-backed initialization path and should not be generalized to all shared-memory failures or to a specific root cause for destination invalidation.

## Search strategy

1. Check shared-memory aggregate initialization for bulk serialization writes through destinations whose validity is not verified at the write site.
2. Trace backing-storage mapping, allocation, and lifetime transitions immediately before native bulk writes.
3. Inspect native buffer-copy or packing paths for invalid-destination handling that converts faults into recoverable errors.
4. Review fuzz-reduced initialization cases involving temporary-resource or storage-lifetime changes for stale destination addresses.

## Evidence

- [#140777](../micro_taxo/gh_140777.md): The sanitizer trace shows aggregate construction reaching a native packing operation whose bulk memory write faults at an unusable high address; discussion indicates the shared-memory construction is the relevant trigger, while the report does not establish a reproducible cause for the invalid destination.

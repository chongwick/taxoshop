# Concurrent bulk initialization of newly allocated object storage overlaps with lock-free inspection of header metadata, allowing transient metadata values to be

A concurrent allocator zeroes an entire object allocation before initializing its ownership and reference metadata, while another thread can inspect those same header fields.

## Precondition

An allocated or reused object address can be inspected concurrently with its initialization, and the header contains metadata that other threads read without taking the allocator's exclusive lock.

## Critical operation

The allocator performs a non-atomic bulk zeroing operation over the complete allocation before explicitly initializing the object header.

## Interference

A concurrent metadata inspection reads header bytes while the bulk write is progressing, so individual fields or multi-byte values can be observed in partially updated states.

## Invalid assumption

It is unsafe to assume that a same-thread header initialization immediately after the bulk write, or atomicity of the reader's loads, prevents a race with the non-atomic clearing operation.

## Failure

The observer can infer a transiently matching or incorrect owner, reference state, or object validity, producing inconsistent concurrent behavior and a data-race or sanitizer report.

## Scope

This is a singleton pattern derived from one report. It is scoped to allocation or reuse paths where concurrency-visible object metadata is bulk-cleared before header initialization and can be inspected concurrently; it does not claim that all allocator zeroing is unsafe.

## Search strategy

1. Check whether allocation-time memset, zeroing, or bulk initialization writes object headers that concurrent lock-free readers may inspect.
2. Trace whether header initialization occurs only after a full-allocation clear and whether the object address can already be reachable by another thread.
3. Search for atomic or lock-free reads of ownership, reference-count, state, or publication fields that overlap byte-wise allocator writes.
4. Verify that bulk initialization is limited to payload bytes after concurrency-visible metadata has been initialized, or is otherwise synchronized with all readers.

## Evidence

- [#130019](../micro_taxo/gh_130019.md): The report documents a non-atomic full-allocation memset racing with concurrent reads of ownership and reference metadata; it supports restricting bulk clearing to payload storage after the header rather than treating the race as harmless.

# Sanitized code consumes data initialized across an uninstrumented library or system-call boundary

A memory-sanitized component reads data whose real bytes are initialized, but whose sanitizer shadow metadata was not propagated across an uninstrumented boundary.

## Precondition

A program enables uninitialized-memory instrumentation while relying on a library or low-level data source that is not instrumented compatibly.

## Critical operation

Instrumented code scans, compares, hashes, or otherwise reads the returned buffer or string-like value.

## Interference

The boundary initializes or fills the actual storage without updating the instrumentation metadata, or metadata from the producing component is unavailable.

## Invalid assumption

The sanitizer's shadow state is assumed to accurately represent the data's real initialization state across every call, library, and system interface.

## Failure

The sanitizer reports a fatal use of uninitialized memory during a valid operation, producing a false positive until the producer is instrumented or the boundary explicitly marks the data initialized.

## Scope

The reports support a pattern specific to shadow-metadata sanitizers such as MSan at uninstrumented library, runtime, or syscall boundaries. They do not establish that every uninitialized-memory report is a false positive or that all boundary crossings require the same repair.

## Search strategy

1. Check every library and runtime dependency on a sanitized link path for compatible sanitizer instrumentation.
2. Inspect system-call and foreign-function boundaries for buffers whose sanitizer initialization metadata is not explicitly propagated.
3. Trace every reported read of a valid buffer back to its producer and compare actual writes with shadow-metadata updates.
4. Add a targeted test that consumes data returned by each uninstrumented boundary under the sanitizer and verify whether explicit metadata marking is required.

## Evidence

- [#135774](../micro_taxo/gh_135774.md): A valid startup key created through code linked from an unsanitized prebuilt runtime was later hashed by instrumented code, exposing missing shadow metadata as an uninitialized read.
- [#140332](../micro_taxo/gh_140332.md): A sanitized extension passed data through an unsanitized cryptographic library, whose comparison path triggered an apparent uninitialized read because the external library was not built with matching instrumentation.
- [#148850](../micro_taxo/gh_148850.md): A system call filled a buffer without sanitizer metadata updates; a later instrumented search treated the valid returned bytes as uninitialized until the buffer was explicitly unpoisoned.

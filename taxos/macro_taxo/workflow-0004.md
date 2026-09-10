# Live memory-mapped persistent storage can be externally truncated before a later update accesses the mapping.

A persistent store remains open while its backing file is externally shortened, and a subsequent operation accesses mapped data using the original layout.

## Precondition

A persistent file-backed store has live memory-mapped contents and assumes the backing file remains sufficiently sized and structurally valid.

## Critical operation

A later update or lookup dereferences mapped storage based on the previously valid file layout.

## Interference

An external actor truncates or otherwise shortens the backing file while the store remains open.

## Invalid assumption

The existing mapping still refers to valid backing storage covering the original addresses and layout.

## Failure

The access produces a fatal storage-library error or process-terminating memory fault instead of a recoverable error.

## Scope

Singleton cluster: scoped to persistent stores using live memory mappings where the backing file may be truncated or shortened externally. The report does not establish a rule for ordinary buffered I/O, file replacement without shrinkage, or every form of mapping invalidation.

## Search strategy

1. Check whether live mappings can outlast validation of the backing file's current size.
2. Check update and lookup paths for mapped-memory dereferences without backing-file length validation.
3. Check whether external truncation or shrinkage is handled before accessing mapped data.
4. Check whether invalidated mappings become recoverable errors rather than fatal faults.

## Evidence

- [#66234](../micro_taxo/gh_66234.md): The report reproduces an open persistent store whose backing file is emptied externally, after which a write reaches invalid mapped storage and terminates the process; disabling mapping avoids the reproduced crash in the described configuration.

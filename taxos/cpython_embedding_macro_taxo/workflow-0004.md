# External truncation of an open memory-mapped file-backed store leaves mapped accesses beyond the shortened backing file vulnerable to fatal process termination.

A file-backed store retains an open, potentially memory-mapped view of its backing file while another actor can replace or truncate that file.

## Precondition

A file-backed store is open with a mapping or equivalent direct access to its backing file, and the backing file can be truncated externally without closing the store.

## Critical operation

A later store operation reads or updates data through the retained backing-file access.

## Interference

An external actor truncates the backing file after the store has been opened.

## Invalid assumption

The operation assumes the retained mapped layout remains backed and valid at its original extent despite external truncation.

## Failure

Accessing the invalidated backing range causes a fatal library error or hardware fault that terminates the process instead of reporting a recoverable storage error.

## Scope

Singleton cluster. This pattern is limited to externally truncated open file-backed stores whose retained direct or memory-mapped access can outlive the backing file's original extent; the report does not establish behavior for other backing-file mutations or all storage libraries.

## Search strategy

1. Check every file-backed mapping operation for backing-file size or identity changes made after the mapping was established.
2. Check update, lookup, enumeration, and maintenance paths for direct mapped reads after external truncation can occur.
3. Check whether externally mutable backing files are protected by locking, ownership constraints, or explicit reopen-and-validate logic.
4. Check fatal-error and signal paths from storage dependencies to ensure damaged backing data is surfaced as a recoverable error where supported.
5. Check configuration paths that enable memory-mapped I/O for a documented crash-tolerance tradeoff and safe fallback behavior.

## Evidence

- [#66234](../micro_taxo/gh_66234.md): An open file-backed store was externally truncated, then a subsequent write caused a fatal read error or bus error; disabling memory-mapped I/O was observed to prevent the crash, though the proposed mitigation was later reverted.

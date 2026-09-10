# Concurrent operations on shared native security state can independently release the same allocation when cleanup ownership and lifetime are not synchronized.

A shared native security/session state is used by overlapping handshake operations, whose failure or completion paths can both reach cleanup for one allocation.

## Precondition

Multiple threads perform concurrent handshakes through the same underlying native security or connection state, with shared allocations reachable by each operation.

## Critical operation

Each handshake invokes native handshake logic that may acquire, mutate, or register cleanup for shared protocol state.

## Interference

One thread releases or invalidates shared state while another handshake still holds a reference to it or remains responsible for cleaning it up.

## Invalid assumption

The handshake paths assume that cleanup ownership is exclusive, or that the shared native state remains alive and coordinated until all concurrent users finish.

## Failure

A later cleanup releases the already-freed allocation again, producing a native double-free and terminating the process under memory-safety checking.

## Scope

This is a singleton report. It supports the concurrency, shared native state, and double-release mechanism, but the report does not establish whether the defect resides in the wrapper or the underlying security library, nor whether every handshake failure path is involved.

## Search strategy

1. Check whether concurrent handshake or negotiation entry points can operate on the same native session or connection object.
2. Trace every error, cancellation, retry, and completion cleanup path for shared allocations and identify whether ownership is exclusive or reference-counted.
3. Verify that native-state teardown is serialized or lifetime-protected until all in-flight operations have exited.
4. Audit wrapper code that releases the GIL or otherwise permits simultaneous native calls while sharing protocol-library state.

## Evidence

- [#140608](../micro_taxo/gh_140608.md): The sanitizer trace shows two worker threads executing the same native secure-handshake path; one freed a large native allocation and the other attempted to free that same address, supporting a concurrent shared-state lifetime or ownership failure.

# Shutdown validation mistakes process-scoped blocked daemon workers for synchronously reclaimable threads

Shutdown validation treats process-scoped daemon workers blocked in accept or request I/O as synchronously leaked, even though their lifecycle ends with the standalone server process. Making cleanup fully synchronous can instead hang when blocked operations lack cooperative cancellation.

## Precondition

A standalone server process uses daemon background workers for connection acceptance and/or request handling, with process exit serving as the intended cleanup boundary.

## Critical operation

The server begins shutdown by signaling its main loop or request handlers while workers remain in blocking listener or connection I/O.

## Interference

The blocking I/O does not observe the shutdown signal until it returns, because the listener or connection is not closed, timed out, or otherwise made cancellation-responsive.

## Invalid assumption

Teardown assumes that every created worker must be synchronously terminated and joined, without accounting for daemon workers whose lifetime is intentionally process-scoped or for uncooperative peers that can keep I/O blocked.

## Failure

Thread-leak instrumentation reports a live or unjoined worker, while attempts to join all workers can delay or hang shutdown and leave process-owned temporary resources behind if the standalone server does not exit.

## Scope

Singleton cluster. The evidence supports a narrowly scoped pattern for standalone, process-bound daemon-worker servers. It does not establish that daemon-thread leaks are harmless in libraries or in-process services, nor that every blocking worker should be exempt from explicit shutdown.

## Search strategy

1. Trace every daemon worker to its blocking accept or connection-I/O operations and identify the actual process or service boundary that ends its lifetime.
2. Check whether shutdown signals can interrupt each blocking operation through listener closure, bounded timeouts, cancellation, or equivalent mechanisms.
3. Inspect teardown instrumentation for assumptions that process-scoped daemon workers must be synchronously joined.
4. Verify that any proposed joins cannot be held indefinitely by an uncooperative connection peer or handler operation.

## Evidence

- [#140267](../micro_taxo/gh_140267.md): Daemon server workers remained blocked in accept or request I/O when shutdown validation reported a thread leak. The report explains that a shutdown event does not cancel every blocking operation and that synchronous joining may hang; worker lifetime was intended to end with the process.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0096](../macro_taxo_before_hybrid/workflow-0096.md)

# A process-scoped background worker performs an indefinitely blocking connection wait, while shutdown signals are checked only outside that wait. The worker can,

A process-scoped background worker performs an indefinitely blocking connection wait, while shutdown signals are checked only outside that wait. The worker can remain alive after the service’s main shutdown path finishes, causing teardown instrumentation to report a thread leak; joining it directly may instead block indefinitely if its wait or downstream I/O has no bounded exit.

## Precondition

A standalone service uses a background worker for blocking connection acceptance, and the worker’s lifetime is tied to process termination or daemon-style cleanup rather than explicit cooperative shutdown.

## Critical operation

The worker enters a blocking accept or receive operation and the service begins shutdown by signaling its main loop and request-processing workers.

## Interference

The blocking operation is not interrupted by the shutdown signal because the listener is not closed, timed out, or otherwise made responsive to cancellation; the worker therefore cannot return to recheck the signal.

## Invalid assumption

Shutdown signaling alone is assumed to terminate every worker, or teardown assumes that every still-live worker must be synchronously joined without accounting for process-scoped daemon semantics and potentially unbounded I/O.

## Failure

Shutdown validation reports a live-worker or thread leak; if cleanup is changed to join the worker synchronously, shutdown can hang when the worker or its request handlers remain blocked.

## Scope

Singleton cluster. This pattern is scoped to standalone, process-bound services using daemon-style workers; in that design, an instrumentation warning may reflect an intentional process-exit cleanup model rather than an externally visible resource leak.

## Search strategy

1. Trace every background worker’s blocking accept or receive call and verify how shutdown interrupts it.
2. Check whether each shutdown signal is observed inside the worker’s blocking loop rather than only by an outer loop.
3. Verify that listener closure, bounded timeouts, cancellation, or equivalent mechanisms make blocked workers exit.
4. Inspect teardown checks and joins for assumptions that process-scoped daemon workers must be synchronously reclaimed.

## Evidence

- [#140267](../micro_taxo/gh_140267.md): The report documents a standalone manager process whose daemon connection-accepting worker blocks in accept, does not observe the shutdown event, and is reported by thread instrumentation as leaked; review feedback also notes that joining blocking handler workers can itself be unreliable.

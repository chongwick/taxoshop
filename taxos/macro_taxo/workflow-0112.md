# A quiescence deadlock caused by acquiring or invoking broader coordination while holding a contended narrow lock.

Concurrent code performs a quiescence-sensitive operation while holding a lock whose waiters are not allowed to reach the required safe point.

## Precondition

A subsystem has a narrow shared mutex and a broader coordination mechanism that pauses or waits for participating workers to reach safe points; contended mutex acquisition can leave a worker attached or otherwise unable to report that safe point.

## Critical operation

A worker holds the narrow mutex while performing an operation that directly requests global quiescence or indirectly acquires a broader coordination lock that can request global quiescence.

## Interference

Another worker holds or waits on the broader coordination state while additional workers block on the narrow mutex without reaching the safe point required by the quiescence operation.

## Invalid assumption

The narrow mutex can safely be held across callbacks, invalidation, lock acquisition, or global coordination, and workers blocked on it will not prevent a global pause from completing.

## Failure

A circular wait forms: the quiescence requester waits for blocked workers, blocked workers wait for the narrow mutex, and the mutex holder waits for the broader coordination or quiescence operation. The system hangs instead of completing.

## Scope

The reports share the quiescence-versus-lock dependency, but differ in shape: one directly invokes global pause while holding the narrow lock, while the other reaches it through a second lock and a lock-order inversion. The pattern is scoped to systems where lock waits can prevent safe-point participation.

## Search strategy

1. Check every operation performed while holding a shared mutex for callbacks, invalidation, registration, or other actions that may acquire another lock.
2. Trace whether waiting for each contended mutex detaches, yields, or otherwise permits the worker to reach global safe points.
3. Check for lock-order inversions between narrow resource locks and broader coordination or state-management locks.
4. Check whether any global pause or quiescence operation can run while a lock needed by its participants is held.
5. Check multi-threaded paths with several workers contending on the same mutex while another worker performs a stop, update, or invalidation operation.

## Evidence

- [#139116](../micro_taxo/gh_139116.md): One worker held a shared tracing-table lock while invoking a tracer change that requested a global pause; another worker had attached and blocked on that lock without detaching, so the pause waited for a worker that could not progress until the lock was released.
- [#151593](../micro_taxo/gh_151593.md): One mutator acquired a shared key-structure mutex and then attempted to acquire a type-management lock; another worker held the type-management lock while requesting global quiescence, and other mutators blocked on the shared mutex without reaching safe points, creating the same circular wait.

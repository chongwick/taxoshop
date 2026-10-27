# Unsynchronized lazy initialization of shared derived state

Concurrent first-use initialization of a shared cache or runtime value is performed with an unsynchronized check-then-compute/publish sequence, sometimes spanning multiple fields or ownership changes.

## Precondition

A shared object, cache slot, or runtime state contains an absent or sentinel-marked derived value that multiple threads can access concurrently, and initialization is deferred until first use without a once protocol, lock, or atomic publication scheme.

## Critical operation

A thread observes the sentinel, computes or fetches the derived value, and publishes it or updates associated metadata and ownership state before returning or using it.

## Interference

Other threads can observe the same sentinel and perform the computation concurrently, publish competing results, read the state while it is being initialized, or race with the associated metadata and reference/ownership updates.

## Invalid assumption

Equivalent results, object immutability, atomicity of an individual pointer or flag, or historical serialization by a global interpreter lock is assumed to make the check, initialization, publication, and ownership bookkeeping safe as one operation.

## Failure

The program has a data race and may expose incompletely published or inconsistently paired state; competing initialization can also leak, mis-account, or incorrectly release resources, producing sanitizer failures, invalid behavior, or crashes.

## Scope

The shared pattern is unsynchronized concurrent first-use initialization or publication of shared derived state. It does not require duplicate computation in every case: one report is primarily a reader-versus-publisher race, and another is eager runtime initialization replacing a lazy global. The umbrella reports also contain unrelated sanitizer findings, which are not generalized here.

## Search strategy

1. Search for shared fields tested against NULL, zero, or a sentinel and assigned by the same first-use path; verify the test and publication are synchronized.
2. Search for lazy initialization that writes a pointer plus length, status, flags, or other metadata; verify readers cannot observe a mixed-generation state.
3. Search for cache fills or external-resource fetches performed after a relaxed cache miss; verify compare-exchange or locking handles losing computations and their ownership.
4. Search for static or runtime globals initialized inside frequently called accessors; verify they are initialized before concurrency begins or protected by a one-time primitive.
5. Search for diagnostic or consistency readers that access fields concurrently with lazy writers; verify they use the same atomic or locking discipline and valid publication ordering.

## Evidence

- [#128013](../micro_taxo/gh_128013.md): Concurrent first access generated a shared encoded representation while its pointer, length, and contents were published in an unsafe order; the fix serialized initialization and published the pointer only after the representation was complete.
- [#128133](../micro_taxo/gh_128133.md): Concurrent first hashing of the same shared value raced on its sentinel-based cached result; atomic cache accesses were required even though the computed hash was deterministic.
- [#128212](../micro_taxo/gh_128212.md): A consistency reader accessed the shared representation pointer concurrently with its publisher without using the required atomic access discipline.
- [#130421](../micro_taxo/gh_130421.md): The report identified lazily initialized shared runtime timebase state as racy and moved its computation into runtime initialization; its broader sanitizer findings include unrelated initialization and object-lifetime races.
- [#153201](../micro_taxo/gh_153201.md): The associated analysis identified concurrent first fetches into shared digest cache slots; atomic publication alone did not resolve the race-loser ownership bookkeeping, which could leave transient reference imbalances and leaks or over-release hazards.
- [#154044](../micro_taxo/gh_154044.md): Concurrent first reads of a shared descriptor property both computed and stored equivalent cached values through an unsynchronized check-then-write, leaking the losing result despite value equivalence.

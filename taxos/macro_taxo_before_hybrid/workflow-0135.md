# An append-like operation consumes an iterator whose reported size estimate is zero even though the iterator can yield elements.

The operation sizes destination storage from an iterator estimate, retains shared zero-capacity empty storage, and writes a yielded element before ensuring capacity.

## Precondition

An iterator or producer supplies an underestimating size hint, reporting zero while still capable of yielding one or more elements.

## Critical operation

An append-like consumer uses that hint to retain shared zero-terminated empty storage and attempts to place the first yielded element into it.

## Interference

The retained storage has no writable element capacity, and the capacity-growth or replacement check occurs only after the first element is prepared for storage.

## Invalid assumption

The consumer treats the advisory size estimate as an accurate indication that no elements will arrive, or as sufficient evidence that the current storage can receive the next element.

## Failure

The first yielded element is written outside the destination allocation, corrupting adjacent memory and causing a buffer-overflow failure instead of safely growing storage.

## Scope

This is a cautiously scoped singleton pattern. The evidence establishes the interaction among an under-reporting iterator hint, shared zero-capacity empty storage, and a pre-growth write; it does not establish that all size-hint consumers or all empty-storage representations are vulnerable.

## Search strategy

1. Check iterator-consuming append paths for size hints used as exact counts or upper bounds.
2. Check zero-size initialization paths for reuse of shared, sentinel, or terminator-bearing storage with no element capacity.
3. Check whether the first element is written before capacity is validated and storage growth or replacement occurs.
4. Check whether adversarial or custom iterators can under-report size while still yielding elements.

## Evidence

- [#143003](../micro_taxo/gh_143003.md): The report shows that a zero size hint from a non-empty iterator led an append operation to use shared zero-terminated empty storage; the first yielded value was written before growth, producing an overflow and corruption risk.

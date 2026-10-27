# Concurrent readers observe shared state before initialization or structural mutation is complete

A shared object, record, or table becomes reachable to concurrent readers before its dependent fields and backing representation are fully initialized, or readers inspect it while construction or structural mutation is still underway. The missing publication ordering or synchronization lets readers observe an intermediate state.

## Precondition

Threads can concurrently reach a shared object, record, or container during its construction, attachment, insertion, resizing, or other mutation, and the implementation lacks one complete protocol covering publication and related state.

## Critical operation

A writer publishes reachability, occupancy, list membership, or another visibility marker before initializing the fields it denotes, or a reader performs lookup or inspection without the lock, atomic ordering, or critical section that synchronizes the complete representation.

## Interference

A concurrent reader observes the published marker or reachable object while dependent fields are still being written, entries are being inserted or resized, or identity metadata is being initialized.

## Invalid assumption

Publication of one pointer, index, list link, scalar, or immutable-looking object is assumed to make the entire referenced state initialized and stable; alternatively, atomicity of an individual field is assumed to protect the coupled representation.

## Failure

Readers can encounter null, incomplete, or internally inconsistent state, producing a data race, transiently changing observations, sanitizer reports, assertions, or a crash instead of a consistent entry or record.

## Scope

Membership was manually restricted to the evidence listed below. The common pattern is premature or insufficiently synchronized visibility of shared state, but the reports show distinct mechanisms: one exposes a table marker before its entry contents, one exposes a half-built object whose representation is still changing, and one exposes a record before scalar identity initialization. They do not establish a stale-or-freed-state mechanism or require ownership leakage in every case; failures range from race reports and inconsistent observations to a crash.

## Search strategy

1. Trace every publication path and verify that a table marker, pointer, list link, or object reference becomes visible only after all fields and dependent storage that readers may access are initialized.
2. Check lock-free lookup and inspection paths for coupled reads of occupancy markers, counters, entry tables, backing storage, and metadata; require one complete synchronization or acquire/release protocol.
3. Audit construction and attachment paths for objects or records that become reachable through registries, tracking lists, callbacks, or user-controlled code before initialization is complete.
4. Distinguish scalar identity publication from structural publication: verify that atomic field access is sufficient for the value-only reader and does not substitute for synchronization of a changing container or record.
5. Check insertion, resize, clear, and attachment interleavings under a race detector for readers that can observe construction-time state.

## Evidence

- [#132869](../micro_taxo/gh_132869.md): A concurrent lookup could observe a hash-table occupancy index before the associated entry key had been initialized because the marker and entry contents were published without the required ordering, leading to an invalid null entry and crash.
- [#151722](../micro_taxo/gh_151722.md): A supposedly immutable object could be leaked while still being populated, allowing length, representation, and hash readers to race construction-time counter updates and table insertion or resizing.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0077](../macro_taxo_before_hybrid/workflow-0077.md)
- [workflow-0081](../macro_taxo_before_hybrid/workflow-0081.md)
- [workflow-0150](../macro_taxo_before_hybrid/workflow-0150.md)

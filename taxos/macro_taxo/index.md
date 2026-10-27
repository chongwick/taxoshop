# Manually constrained hybrid workflow taxonomy

The original top five memberships and IDs are restored exactly. Remaining hybrid groups are retained where possible; the residual shared-state group is split by original source families. This is a manually constrained partition, not an unconstrained clustering result.

116 clusters; 363 workflows.

| Cluster | Issues | Pattern |
|---|---:|---|
| [workflow-0014](workflow-0014.md) | 38 | Borrowed or derived handles are used after reentrancy, concurrency, mutation, or teardown invalidates their owner or backing storage. |
| [workflow-0080](workflow-0080.md) | 22 | Callback re-entrancy invalidates borrowed state or backing storage during a native operation |
| [workflow-0137](workflow-0137.md) | 20 | Reentrant user-code execution invalidates native state before later use |
| [workflow-0077](workflow-0077.md) | 11 | Concurrent contexts access shared process-wide state without a complete synchronization or publication protocol |
| [workflow-0091](workflow-0091.md) | 10 | Error-path ownership loss in native operations |
| [workflow-0079](workflow-0079.md) | 9 | Ownership-bound cleanup paths fail to reclaim direct or nested allocations |
| [workflow-0017](workflow-0017.md) | 8 | Unchecked representation assumptions across dynamic boundaries |
| [workflow-0064](workflow-0064.md) | 8 | Lifecycle ownership diverges across reusable isolated contexts |
| [workflow-0100](workflow-0100.md) | 8 | Concurrent access to mutable shared state without effective synchronization or lifetime protection |
| [workflow-0241](workflow-0241.md) | 7 | Concurrent unsynchronized access to shared mutable storage or state |
| [workflow-0036](workflow-0036.md) | 6 | Malformed compact location metadata reaches unchecked or assertion-only decoders |
| [workflow-0090](workflow-0090.md) | 6 | Unsynchronized lazy initialization of shared derived state |
| [workflow-0118](workflow-0118.md) | 6 | Generated optimized state has mismatched ownership across lifecycle handoffs |
| [workflow-0166](workflow-0166.md) | 6 | Unchecked size, width, and position metadata drives native writes beyond allocated storage |
| [workflow-0138](workflow-0138.md) | 5 | Error-path cleanup of partially acquired state is incomplete or misdirected |
| [workflow-0158](workflow-0158.md) | 5 | Optimized runtime state remains usable after its assumptions require invalidation |
| [workflow-0005](workflow-0005.md) | 4 | Zero-count memory transfer through absent or invalid storage |
| [workflow-0008](workflow-0008.md) | 4 | Concurrent consumers of a shared iterator race traversal-state updates with backing-state ownership or cleanup. |
| [workflow-0024](workflow-0024.md) | 4 | Layered parser error paths continue after lower-level failure state becomes invalid |
| [workflow-0042](workflow-0042.md) | 4 | Consumers read storage whose initialization is implicit, partial, or omitted, relying on later arithmetic or platform guarantees to make the read harmless |
| [workflow-0044](workflow-0044.md) | 4 | Sanitizer leak checking aborts otherwise successful short-lived runtime or build subprocesses |
| [workflow-0050](workflow-0050.md) | 4 | Incompatible function prototype at an indirect callback or slot boundary hidden by type erasure, casts, or dispatch metadata |
| [workflow-0052](workflow-0052.md) | 4 | Unchecked failure results contaminate downstream processing and error-recovery paths |
| [workflow-0057](workflow-0057.md) | 4 | Concurrent non-atomic mutation or initialization of concurrency-visible object metadata races with ownership and lifecycle inspection |
| [workflow-0061](workflow-0061.md) | 4 | Instrumentation compatibility failures contaminate configuration probes or target linkage |
| [workflow-0073](workflow-0073.md) | 4 | Unchecked numeric values cross native boundaries without semantic or size validation |
| [workflow-0188](workflow-0188.md) | 4 | Empty-result operations leak invalid metadata into nonempty validation or access paths |
| [workflow-0210](workflow-0210.md) | 4 | Unchecked consumption of absent or inconsistent metadata resolution results |
| [workflow-0242](workflow-0242.md) | 4 | Unsynchronized concurrent access to replaceable, reference-owned object fields |
| [workflow-0001](workflow-0001.md) | 3 | Runtime execution state crosses thread or process boundaries without revalidation, causing identity or lifetime failures |
| [workflow-0029](workflow-0029.md) | 3 | Generated configuration scripts trust unvalidated external tool commands or dialects. |
| [workflow-0030](workflow-0030.md) | 3 | Signed left shifts used to construct packed or bit-oriented values can trigger undefined behavior before the intended representation is finalized. |
| [workflow-0033](workflow-0033.md) | 3 | Optional or uninitialized pointer state is converted with pointer arithmetic before its null/absence state is handled. |
| [workflow-0049](workflow-0049.md) | 3 | Fixed wall-clock test budgets can make asynchronous behavior flaky when scheduling or instrumentation delays progress. |
| [workflow-0058](workflow-0058.md) | 3 | Unsafe typed diagnostic formatting on exceptional paths |
| [workflow-0109](workflow-0109.md) | 3 | Sanitized code consumes data initialized across an uninstrumented library or system-call boundary |
| [workflow-0114](workflow-0114.md) | 3 | Using raw storage or an address with insufficient alignment for a stricter-aligned typed object or access |
| [workflow-0125](workflow-0125.md) | 3 | Availability detection and consumer guards do not match the exact interface entity they expose |
| [workflow-0140](workflow-0140.md) | 3 | Externally tampered executable representations bypass invariant enforcement and reach trusted runtime consumers |
| [workflow-0147](workflow-0147.md) | 3 | Ownership or representation invariants fail across managed-object boundaries |
| [workflow-0174](workflow-0174.md) | 3 | Native consumers trust extension-controlled results without validating their extent or shape |
| [workflow-0223](workflow-0223.md) | 3 | Failure cleanup acts on ownership or destructor state that was not established by the failed operation |
| [workflow-0226](workflow-0226.md) | 3 | Unchecked boundary state reaches representation- or arithmetic-sensitive low-level operations |
| [workflow-0009](workflow-0009.md) | 2 | Signed overflow in derived safety values defeats validation or bounded operation |
| [workflow-0010](workflow-0010.md) | 2 | Unchecked floating-point demotion before representability validation |
| [workflow-0013](workflow-0013.md) | 2 | Bounded instruction-stream consumers dereference an instruction after reaching the stream boundary because end-of-sequence validation is missing or bypassed. |
| [workflow-0021](workflow-0021.md) | 2 | Extreme-allocation tests assume environment-independent recoverable failure. |
| [workflow-0028](workflow-0028.md) | 2 | Forked child inherits live process/thread state that ordinary shutdown cannot reclaim under leak detection |
| [workflow-0040](workflow-0040.md) | 2 | Boundary-unsafe speculative lookahead in text processing. |
| [workflow-0046](workflow-0046.md) | 2 | Auxiliary lifetime or version metadata remains apparently valid after the object, backing mapping, or hierarchy state it describes has changed. |
| [workflow-0059](workflow-0059.md) | 2 | Compiler optimization can precede a dependent convergence or legality check, leaving downstream invariants to process transformed or incomplete state |
| [workflow-0067](workflow-0067.md) | 2 | Static special instances are exposed to collector traversal despite lacking the ordinary object layout. |
| [workflow-0074](workflow-0074.md) | 2 | Instrumented fatal diagnostics break termination progress |
| [workflow-0104](workflow-0104.md) | 2 | Sanitizer exposure of nonportable fault injection and signature-unsafe callback dispatch |
| [workflow-0105](workflow-0105.md) | 2 | Concurrent operations access coupled shared state without synchronizing the complete state transition |
| [workflow-0112](workflow-0112.md) | 2 | A quiescence deadlock caused by acquiring or invoking broader coordination while holding a contended narrow lock. |
| [workflow-0126](workflow-0126.md) | 2 | Concurrent readers observe shared state before initialization or structural mutation is complete |
| [workflow-0153](workflow-0153.md) | 2 | Reentrant finalization changes teardown-owned reachability before cleanup completes |
| [workflow-0156](workflow-0156.md) | 2 | Teardown-ordering retains callback-connected module runtime graphs |
| [workflow-0168](workflow-0168.md) | 2 | Auxiliary per-thread tracing state is omitted from an alternate thread-teardown path |
| [workflow-0172](workflow-0172.md) | 2 | Optimized execution crosses an instrumentation, exceptional-transfer, or fallback boundary without synchronizing speculative stack state |
| [workflow-0193](workflow-0193.md) | 2 | Unchecked dynamic values enter integer-specialized paths without representation validation |
| [workflow-0207](workflow-0207.md) | 2 | Resource ownership is lost when initialization or replacement overwrites the only cleanup handle for an earlier allocation. |
| [workflow-0215](workflow-0215.md) | 2 | Retained derived state or mapped-buffer access reaches storage after its owner or backing resource becomes invalid |
| [workflow-0002](workflow-0002.md) | 1 | Literal reserved marker in display text is misinterpreted as a formatting directive |
| [workflow-0011](workflow-0011.md) | 1 | Heterogeneous numeric equality comparisons can expose an intermittent platform-sensitive memory-safety defect. |
| [workflow-0022](workflow-0022.md) | 1 | Forked child thread creation can deadlock in non-fork-safe runtime instrumentation. |
| [workflow-0025](workflow-0025.md) | 1 | Generated derived-class callables resolve inherited deferred annotations in the wrong namespace. |
| [workflow-0026](workflow-0026.md) | 1 | Large whole-program link-time optimization on an architecture with limited branch displacement is applied to a sufficiently large codebase. |
| [workflow-0034](workflow-0034.md) | 1 | Instrumented allocation crosses a custom allocator’s ownership-probe boundary. |
| [workflow-0037](workflow-0037.md) | 1 | Expanding a bounded diagnostic without worst-case length accounting can truncate existing information. |
| [workflow-0045](workflow-0045.md) | 1 | Pre-dispatch validation assumes current metadata on immutable executable artifacts |
| [workflow-0047](workflow-0047.md) | 1 | A test-suite environment-integrity check detects a process-wide environment mutation left behind by executed test or support code. |
| [workflow-0056](workflow-0056.md) | 1 | Invalid lexer/tokenizer buffer offsets produce pointer-index overflow |
| [workflow-0075](workflow-0075.md) | 1 | Concurrent asynchronous notifications reenter mutable callbacks without a nesting guard |
| [workflow-0076](workflow-0076.md) | 1 | Unrestricted address discovery selects a protocol family unsupported by the runtime |
| [workflow-0081](workflow-0081.md) | 1 | A capacity-sensitive I/O test derives its workload from a reported external-buffer size and uses that single estimate to trigger backpressure. |
| [workflow-0083](workflow-0083.md) | 1 | A fixed-size alternate signal stack is allocated without validating worst-case signal-handler stack usage; signal-path execution can corrupt the heap-backedっ |
| [workflow-0084](workflow-0084.md) | 1 | Dependency contract drift makes compatibility tests stale |
| [workflow-0087](workflow-0087.md) | 1 | Generated control flow retains unreachable operations after termination or configuration folding |
| [workflow-0088](workflow-0088.md) | 1 | Parallel instrumented tests expose environment-sensitive subprocess failures |
| [workflow-0094](workflow-0094.md) | 1 | Include-path ordering selects stale external configuration over the current generated header |
| [workflow-0096](workflow-0096.md) | 1 | Independent compiler-capability checks redefine the same configuration symbol |
| [workflow-0097](workflow-0097.md) | 1 | Shutdown/finalization races with residual worker activity on shared runtime or dependency state |
| [workflow-0110](workflow-0110.md) | 1 | A deep-recursion test runs under a memory-safety instrumentation mode that its skip guard does not recognize. |
| [workflow-0111](workflow-0111.md) | 1 | An instrumentation or diagnostic mode unconditionally replaces an explicitly selected compatible subordinate configuration with its own default. |
| [workflow-0120](workflow-0120.md) | 1 | Unnecessary tracking of immutable acyclic containers increases garbage-collection work |
| [workflow-0127](workflow-0127.md) | 1 | Shutdown validation mistakes process-scoped blocked daemon workers for synchronously reclaimable threads |
| [workflow-0129](workflow-0129.md) | 1 | Unsupported target accepted for optional code generation until artifact generation fails |
| [workflow-0132](workflow-0132.md) | 1 | Null string storage crosses a foreign-function boundary that requires a valid buffer |
| [workflow-0135](workflow-0135.md) | 1 | Collector traversal reaches objects published before their fields are initialized |
| [workflow-0149](workflow-0149.md) | 1 | An enumeration walks a registry containing inactive tombstones while sizing output only for active entries. |
| [workflow-0150](workflow-0150.md) | 1 | A low-level structured-data encoder accepts an unvalidated initial nesting level that is inconsistent with its formatting-cache contents. |
| [workflow-0151](workflow-0151.md) | 1 | A legacy global-registration path is invoked for a component created with an incompatible managed state layout. |
| [workflow-0162](workflow-0162.md) | 1 | Incremental byte-reader boundary checks use a string-derived offset that can remain zero after embedded-NUL input |
| [workflow-0163](workflow-0163.md) | 1 | Incomplete validation of representation-sensitive restored state enables later low-level crash |
| [workflow-0165](workflow-0165.md) | 1 | A callback-driven streaming decoder underestimates output capacity when recovery both emits replacement text and resumes from an earlier input position. |
| [workflow-0169](workflow-0169.md) | 1 | Toolchain and instrumentation combinations leave a generated-code target unusable during bootstrap |
| [workflow-0179](workflow-0179.md) | 1 | Diagnostic metadata lookup uses an instruction representation outside the table index domain |
| [workflow-0180](workflow-0180.md) | 1 | A low-level instruction record is constructed with an operation whose contract disallows an operand, but the record carries a nonzero operand value. |
| [workflow-0200](workflow-0200.md) | 1 | Lock-handoff assertions assume a held state that concurrent release can already change |
| [workflow-0205](workflow-0205.md) | 1 | Uninstrumented dependency synchronization produces misleading sanitizer race reports |
| [workflow-0206](workflow-0206.md) | 1 | Trace-size configuration exceeds generated-code metadata capacity |
| [workflow-0214](workflow-0214.md) | 1 | Truthiness dispatch omits a symbolic value category and reads an incompatible representation |
| [workflow-0216](workflow-0216.md) | 1 | Unvalidated mutation of an executable instruction stream exposes a metadata-only placeholder to instruction dispatch. |
| [workflow-0221](workflow-0221.md) | 1 | Instrumented capability probes can hang during platform/runtime startup before application code executes. |
| [workflow-0232](workflow-0232.md) | 1 | Fixed-depth recursion boundary tests become stale when build-time instrumentation or hardening changes effective recursion capacity. |
| [workflow-0233](workflow-0233.md) | 1 | Concurrent traversal uses runtime-owned records without stable references or teardown exclusion |
| [workflow-0239](workflow-0239.md) | 1 | A logically dead object remains collector-visible across interruptible destruction |
| [workflow-0240](workflow-0240.md) | 1 | A nested-interpolation tokenizer updates delimiter-depth state for a closing delimiter before validating that the delimiter has a matching opener, allowing a-; |
| [workflow-0243](workflow-0243.md) | 1 | Concurrent evaluation loses shared interrupt state |
| [workflow-0244](workflow-0244.md) | 1 | Unsynchronized inspection of concurrently updated synchronization state |
| [workflow-0245](workflow-0245.md) | 1 | Concurrent handshake cleanup double-frees shared native state |
| [workflow-0246](workflow-0246.md) | 1 | Concurrent container mutation races with size inspection |
| [workflow-0247](workflow-0247.md) | 1 | Concurrent reinitialization invalidates a reader's prior bounds check |
| [workflow-0248](workflow-0248.md) | 1 | Concurrent handshakes race on shared connection state |

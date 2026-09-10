# Fixed wall-clock test budgets can make asynchronous behavior flaky when scheduling or instrumentation delays progress.

Fixed wall-clock test budgets can make asynchronous behavior flaky when scheduling or instrumentation delays progress.

## Precondition

A test starts asynchronous work and uses a short fixed timeout or fixed-duration polling window before checking intermediate results or final output.

## Critical operation

The test waits for early completion, readiness, or observable output, then proceeds to assertions or deliberately triggers termination when that time budget expires.

## Interference

System load, parallel execution, process-launch latency, or runtime instrumentation delays worker startup and progress beyond the test's fixed wall-clock window.

## Invalid assumption

The expected milestone or output must be observable within that fixed duration regardless of execution environment.

## Failure

The test observes no or only partial results, times out, or terminates the target before its expected output is available, and reports a failure even though the asynchronous operation may still be behaving correctly.

## Scope

The reports share timing-sensitive asynchronous tests, but the interference affects different milestones: worker startup, readiness signaling, and target completion/output. The pattern does not require an actual timeout exception; premature fixed-time termination is included.

## Search strategy

1. Inspect tests for hard-coded short timeouts around asynchronous startup, readiness, completion, or result collection.
2. Check for fixed sleep durations or bounded polling loops followed by assertions about output, result counts, or process state.
3. Look for test cleanup or quit logic that fires after elapsed time rather than after an explicit completion/readiness signal.
4. Verify that sanitizer, tracing, parallel, and heavily loaded environments can extend the operation beyond the test's timing assumptions.

## Evidence

- [#110097](../micro_taxo/gh_110097.md): A concurrent result test expected immediately completable work to produce two results before a fixed deadline, but loaded systems delayed worker launch so the deadline yielded zero or one result.
- [#143442](../micro_taxo/gh_143442.md): A readiness wait used a fixed short timeout, and runtime instrumentation plus parallel execution delayed startup enough to cause a readiness timeout.
- [#150966](../micro_taxo/gh_150966.md): A live subprocess test quit after a fixed simulated interval, and sanitizer or loaded execution delayed target completion so expected failure output had not yet been collected.

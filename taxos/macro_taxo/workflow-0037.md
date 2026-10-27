# Expanding a bounded diagnostic without worst-case length accounting can truncate existing information.

A human-readable diagnostic has a hard size limit and already combines variable-length version, timestamp, revision, and toolchain fields. Adding configuration-dependent build metadata increases the same output without guaranteeing room for every field.

## Precondition

A diagnostic is assembled into fixed-capacity storage or another hard display limit, with multiple variable-length fields already present.

## Critical operation

Append build, configuration, optimization, or instrumentation details to that existing diagnostic format.

## Interference

The added metadata competes with existing fields for bounded capacity, and its length varies with enabled options and compiler or toolchain details.

## Invalid assumption

Assume the prior capacity remains sufficient for every combination of existing fields and newly added metadata, without checking worst-case output length or truncation.

## Failure

The formatter truncates the diagnostic, potentially removing build or compiler information and producing incomplete or misleading output; a separate diagnostic channel avoids enlarging the constrained string.

## Scope

This singleton pattern is scoped to one report about expanding a bounded version/build diagnostic. The report supports both direct truncation from shared capacity and the safer boundary of using a separate channel; it does not establish a broader rule about all diagnostic systems.

## Search strategy

1. Inspect fixed-size diagnostic buffers and verify capacity against the maximum length of every existing and newly added field.
2. Trace formatted diagnostic expansions and calculate worst-case output length across version, revision, timestamp, toolchain, and configuration combinations.
3. Check whether bounded formatting APIs report, test, or otherwise handle truncation after new fields are appended.
4. Review whether detailed metadata can be emitted through a dedicated diagnostic channel when the primary display format cannot guarantee complete output.

## Evidence

- [#100086](../micro_taxo/gh_100086.md): An attempted change appended configuration-dependent build details to a fixed-capacity version/build string, and the reported display truncated the ending of the build description or compiler information. The accepted follow-up emitted the details in a separate test-runner diagnostic instead.

## Source taxonomy

Adapted to the hybrid cluster membership from these archived macro entries:

- [workflow-0033](../macro_taxo_before_hybrid/workflow-0033.md)

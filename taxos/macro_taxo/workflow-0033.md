# Appending variable-length build or configuration metadata to a compact diagnostic string whose storage limit was sized for the preexisting fields can truncate,1

A compact diagnostic already combines version, revision, timestamps, and toolchain metadata in fixed-capacity storage. A change adds configuration-dependent build details to that same formatted output.

## Precondition

A human-readable diagnostic is assembled in a fixed-size buffer or other hard output limit, and its existing fields already have variable-length content.

## Critical operation

Append additional build, configuration, optimization, or instrumentation metadata to the existing diagnostic format.

## Interference

The new metadata competes with the existing version and toolchain fields for the same bounded capacity; the combined length varies with enabled options and compiler details.

## Invalid assumption

Assume the prior capacity or a static maximum remains sufficient for every combination of existing and newly appended fields.

## Failure

The formatter truncates the diagnostic, potentially dropping part of the new build description or existing toolchain information and producing incomplete or misleading output.

## Scope

This is a singleton cluster, so the pattern is scoped to the one documented attempt to expand a bounded version/build diagnostic. The report also shows a boundary: moving detailed metadata to a dedicated diagnostic channel avoids enlarging the constrained string.

## Search strategy

1. Inspect fixed-size diagnostic buffers and verify their capacity against the maximum length of every existing and newly added field.
2. Trace every formatted diagnostic expansion and calculate worst-case output length for combinations of version, revision, timestamp, toolchain, and configuration metadata.
3. Check whether bounded formatting APIs report or test truncation after new fields are appended.
4. Review changes that add variable-length build or environment details to single-line version, startup, or banner output and require an alternate channel when the bound cannot be guaranteed.

## Evidence

- [#100086](../micro_taxo/gh_100086.md): The attempted change appended configuration-dependent build details to an existing version/build-info string stored in fixed-capacity storage; the reported output was truncated, losing the end of the build description or compiler information. The follow-up placed the details in a separate test-runner diagnostic instead of extending the shared line.

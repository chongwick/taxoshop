# New CPython sanitizer findings

Audit date: 2026-09-10

This directory records two crash reproducers that are new to this repository's
taxonomy. Both fit `taxos/macro_taxo/workflow-0080.md`: callback re-entrancy
invalidates native state that the outer operation continues to use.

The reproducers are:

* `gh-139071`: recursive equality callbacks corrupt a set's accounting and
  make deallocation read past the table.
* `gh-145105`: a re-entrant iterator resets a CSV reader's field list while
  the outer parse still appends to it.

Each finding contains the reproducer, local native-run evidence, the complete
ASan output copied from the upstream report, and the upstream deduplication
status. The upstream reports are linked because the sanitizer logs are
reference evidence, not logs generated in this workspace: Docker daemon access
was denied when the requested sanitizer build was attempted.

The findings are new relative to `taxos/bugs.txt`, `taxos/micro_taxo/`, and
`taxos/workflow_signatures/`; they are not claims that the defects were unknown
to CPython maintainers.

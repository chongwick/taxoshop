# Source-First Micro-Taxos and Fingerprints

## Goal

Replace the analytical micro-taxonomy artifact with a source-first archive of
the GitHub issue. For every issue URL, retain the complete issue API record,
all issue comments, readable verbatim content, and evidence-only fix
references. Generate a separate analytical fingerprint only after its source
micro-taxo has been written.

## Artifact Layout

`workdir_python/micro_taxos/gh_<issue-number>.md` contains one GitHub issue
record. `workdir_python/fingerprints/gh_<issue-number>.md` contains the
matching fingerprint. Both filenames use the same issue number.

The existing `workdir_python/open_github_issues.txt` remains the list of
issues whose GitHub API state is `open` at generation time.

## Micro-Taxo Format

The template is a deterministic source-record format rather than an analysis
prompt. Each generated document contains:

1. The issue number, title, URL, state, and retrieval timestamp.
2. Readable metadata from the issue API response, including author, labels,
   assignees, milestone, lock state, timestamps, and closure metadata when
   available.
3. The issue body exactly as supplied by GitHub.
4. Every issue comment in GitHub order, including each comment's author, URL,
   creation/update timestamps, and body exactly as supplied by GitHub.
5. Fix information composed only of GitHub pull-request and commit URLs found
   verbatim in the issue body or comments, each cited to its source. GitHub
   closure metadata is included separately. The artifact does not identify a
   link as the fix unless the source text explicitly does so.
6. Full unmodified JSON records for the issue and every retrieved comment so
   all available API fields survive schema changes and formatting choices.

No generated micro-taxo contains a bug summary, inferred root cause,
reproducer, failure classification, pattern tags, macro-taxonomy signal, or
other analysis.

## Processing Sequence

For each input issue, in input order:

1. Fetch the issue record and paginate through all comments.
2. Write the deterministic micro-taxo atomically.
3. Give the completed micro-taxo and `templates/fingerprint-template.md` to a
   read-only Codex thread, which returns only a filled fingerprint document.
4. Validate and atomically write the fingerprint.
5. Continue to the next issue regardless of earlier per-issue failures.

The open-issues report is written after the batch. A fetched open issue stays
in that report even if fingerprint generation fails.

## Error Handling

GitHub retrieval failure prevents both artifacts for that issue and is listed
in the batch failure output. A fingerprint failure leaves the completed
micro-taxo in place, records the error, and does not prevent subsequent
issues from being processed. Atomic writes prevent partial artifacts.

## Verification

Tests use fake GitHub and Codex clients to assert that one issue produces the
source micro-taxo before its matching fingerprint, that verbatim content and
raw records are retained, and that failures follow the specified ordering and
continuation behavior.

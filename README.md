# taxoshop

Taxoshop is a research workbench for taxonomy-guided runtime audits. It collects
known CPython issues, extracts recurring failure workflows, and turns them into
pattern descriptions and search strategies for finding new bugs. Docker builds
provide instrumented CPython, CRuby, and PHP runtimes for checking candidates.

The checked-in taxonomy is CPython-focused: **363 issue workflows grouped into
116 pattern families**. It covers memory safety, undefined behavior, concurrency,
ownership, and related runtime and tooling failures. The current grouping is a
manually constrained hybrid partition, with the original top five memberships and
IDs restored; rerunning automatic clustering does not reproduce that curation.

## Repository map

| Path | Purpose |
| --- | --- |
| [`taxos/bugs.txt`](taxos/bugs.txt) | Input list of CPython GitHub issues. |
| [`taxos/micro_taxo/`](taxos/micro_taxo/) | Per-issue Markdown reports and cached source evidence under `sources/`. |
| [`taxos/workflow_signatures/`](taxos/workflow_signatures/) | Per-issue JSON signatures, authoritative `clusters.json`, and clustering artifacts. |
| [`taxos/macro_taxo/index.md`](taxos/macro_taxo/index.md) | Human-readable catalog of pattern families; each family has Markdown and JSON descriptions. |
| [`generate_reports.py`](generate_reports.py) | Fetches GitHub issues, comments, attachments, and linked fixes, then renders reports. |
| [`generate_workflow_signatures.py`](generate_workflow_signatures.py) | Generates signatures with Codex, clusters CPU embeddings, and reviews memberships with Codex. |
| [`generate_macro_taxonomy.py`](generate_macro_taxonomy.py) | Generates pattern descriptions and an index from workflow clusters and issue evidence. |
| [`tally_bugs.py`](tally_bugs.py) | Prints the 20 largest families by saved signature membership. |
| [`Dockerfile`](Dockerfile) | CPython ASan/UBSan, TSan, free-threaded TSan, and debug build targets. |
| [`Dockerfile.cruby`](Dockerfile.cruby), [`Dockerfile.php`](Dockerfile.php) | CRuby and PHP ASan/UBSan builds. |
| [`taxoshop_va.py`](taxoshop_va.py) | Experimental budgeted audit runner using the Claude Agent SDK. |
| [`STARTUP.md`](STARTUP.md) | Detailed CPython audit procedure and workspace conventions. |

Runtime source checkouts and `audit<N>/` workspaces are not included. Some paths,
version stamps, and historical references in `STARTUP.md` describe earlier local
workspaces rather than files in this checkout.

## Explore the taxonomy

Run commands from the repository root. Reading the reports requires no setup;
ranking families uses only the Python standard library:

```bash
python3 tally_bugs.py
```

Start with the [pattern index](taxos/macro_taxo/index.md), then read a family's
precondition, critical operation, interference, invalid assumption, failure,
search strategy, and evidence. For example:

- [workflow-0014](taxos/macro_taxo/workflow-0014.md): borrowed or derived handles used after their owners or backing storage are invalidated.
- [workflow-0080](taxos/macro_taxo/workflow-0080.md): callback reentrancy invalidating native state.
- [workflow-0137](taxos/macro_taxo/workflow-0137.md): reentrant user code invalidating state before later use.

The issue numbers in each family connect back to `micro_taxo/gh_<issue>.md` and
`workflow_signatures/gh_<issue>.json`. Family sizes count known examples; they do
not measure the likelihood of finding a new bug.

## Build and run instrumented runtimes

Docker and network access are required to build the images. Source is fetched
inside each build, so a host checkout is not needed to run an interpreter.

### CPython

```bash
docker build --target asan-ubsan -t taxoshop/cpython-asan-ubsan:current .
docker run --rm taxoshop/cpython-asan-ubsan:current ./python -V
docker run --rm taxoshop/cpython-asan-ubsan:current git rev-parse HEAD
```

Reuse an existing image when appropriate, but record its revision. Docker may
cache the source-fetch layer; use `--no-cache` when deliberately refreshing the
upstream checkout. The default reference is `origin/main`. `CPYTHON_REF` must
resolve within the fetched main-branch history, whose depth is controlled by
`CPYTHON_HISTORY_DEPTH` (default `5000`).

| Target | Configuration |
| --- | --- |
| `asan-ubsan` | GCC, AddressSanitizer and UndefinedBehaviorSanitizer, without pymalloc. |
| `tsan` | Clang ThreadSanitizer with the GIL enabled. |
| `tsan-ft` | Clang ThreadSanitizer with `--disable-gil` and `PYTHON_GIL=0`. |
| `vanilla` | GCC debug build with `--with-pydebug`, without sanitizers. |
| `default` | Alias of `asan-ubsan`, selected when `--target` is omitted. |

All targets use `/src/cpython` as the working directory. Pass `./python` explicitly
when running the ASan/UBSan image. Its environment sets `PYTHONMALLOC=malloc`,
disables leak detection, and halts on ASan/UBSan errors with symbolized output.

For example, after placing a reproducer at `audit1/repro/candidate.py`:

```bash
mkdir -p audit1/findings audit1/logs audit1/repro
docker run --rm -v "$PWD/audit1:/audit" \
  taxoshop/cpython-asan-ubsan:current ./python /audit/repro/candidate.py \
  > audit1/logs/candidate.txt 2>&1
```

Run reproducers in separate processes and retain full output. A crash alone is
not sanitizer confirmation; inspect the diagnostic and establish its root cause.

### CRuby and PHP

```bash
docker build -f Dockerfile.cruby -t taxoshop/cruby-asan-ubsan:current .
docker run --rm taxoshop/cruby-asan-ubsan:current /src/ruby/ruby -e 'puts :ok'

docker build -f Dockerfile.php -t taxoshop/php-asan-ubsan:current .
docker run --rm taxoshop/php-asan-ubsan:current /src/php-src/sapi/cli/php -v
```

Both default to `master`; select a branch or tag with `--build-arg RUBY_REF=...`
or `--build-arg PHP_REF=...`. PHP disables Zend's allocator with `USE_ZEND_ALLOC=0`
so allocations are visible to ASan. These Dockerfiles complement the CPython
corpus; Ruby and PHP taxonomies are not bundled.

## Regenerate taxonomy artifacts

The generation scripts require Python 3.10+. Evidence collection uses the `gh`
CLI authenticated for GitHub and `curl` for attachments. Signature and macro
entry generation require an authenticated Codex installation and `openai-codex`;
embedding clustering also requires `sentence-transformers` and scikit-learn.
There is no pinned dependency manifest in this repository.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install openai-codex sentence-transformers scikit-learn

# Preview pending work without model calls or clustering.
python generate_workflow_signatures.py --dry-run
python generate_macro_taxonomy.py --dry-run
```

The pipeline is:

```text
bugs.txt → micro_taxo reports → workflow signatures → clusters → macro_taxo patterns
```

To run it, the following commands fetch evidence, invoke models, and write artifacts:

```bash
python generate_reports.py
python generate_workflow_signatures.py
python generate_macro_taxonomy.py
```

`generate_reports.py` runs all stages by default, or accepts `--sources`,
`--attachments`, `--fixes`, and `--render` to select stages. Signature generation
supports `--only`, `--limit`, and `--force`; these restrict generation only.
Clustering and membership review always consider all saved signatures.
`--recluster-only` skips generation, and `--restart-review` rebuilds clustering
and review instead of resuming matching checkpoints. The embedding model
downloads on first use.

Both model-driven generators accept `--model`. Macro generation also accepts
`--only`, `--limit`, `--force`, `--workflows`, and `--output`. Its `--corpus ruby`
option expects separately supplied Ruby reports and clusters; the included
signature generator processes CPython only.

Regeneration can replace curated memberships and descriptions. Preserve the
current artifacts before reclustering; the scripts do not implement the manual
constraints recorded in the checked-in index.

## Audit workflow and runner status

Follow the procedure in [`STARTUP.md`](STARTUP.md): use ordinary Python
reproducers without `ctypes`, confirm candidates under sanitizers, and check
upstream issues and prior findings for duplicates before reporting. Keep each
audit's notes, findings, full logs, and reproducers together:

```text
audit<N>/
├── NOTES.md
├── findings/
├── logs/
└── repro/
```

Record the parent pattern ID, runtime revision, root cause, minimal reproducer,
sanitizer output, and duplicate analysis for each confirmed finding.

`taxoshop_va.py` is an experimental unattended runner with a CPython-specific
prompt. It uses `claude-agent-sdk` and `anyio`, accepts a repository path plus
`--budget` (default `$20`), `--model`, and `--timeout-hours` (default `8`), and
writes timestamped JSONL logs in the launch directory. It resumes sessions until
a budget, timeout, stall, error, or round limit ends the run.

**The runner currently needs repair before use:** `make_options()` references
`APPEND`, but its definition is commented out, causing a `NameError` when the
first round starts. It also configures `bypassPermissions`, so any future run
should use an environment intended for unattended execution. Cleanup only
removes containers labeled `taxoshop-audit=1`; the instruction to apply that label
is in the commented-out block.

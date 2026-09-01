# SQLite Bug Taxonomy

A reproducible pipeline that (1) conceptually modularizes the SQLite source
tree, (2) scrapes the [SQLite Bug Forum](https://sqlite.org/bugs/forum),
(3) filters invalid reports, and (4) profiles each bug into a **2-D taxonomy
(module × bug-class)** plus an **adjacency index** for steering an AI agent
toward bugs adjacent to a known one.

Built against **SQLite 3.54.0** (the tree in `../sqlite`).

## Pipeline

```
build_modules.py        Phase 1  source tree      -> modules.json
build_symbol_index.py   (aux)    source tree      -> symbols.json   (func -> module)
scrape.py               Phase 2  /bugs/forum      -> data/threads.jsonl
classify.py             Phase 3+4 threads+modules -> data/bugs.jsonl, out/*
```

Run the whole thing:

```bash
python3 build_modules.py --src ../sqlite
python3 build_symbol_index.py --src ../sqlite
python3 scrape.py           # ~277 threads, disk-cached & resumable, rate-limited
python3 classify.py
```

Only the standard library is required (no third-party deps).

## Phase 1 — Modularization (`modules.json`)

Every shipped `src/*.c` and `ext/**` file is assigned to one of **37 modules**
grouped into architectural **layers** following the canonical pipeline
(tokenizer → parser → codegen → optimizer → VDBE → vtab → storage → OS →
types/functions → memory → util → API → extensions). Generated from rules, so
it re-derives cleanly against a future SQLite version. `file_to_module` is the
resolver the classifier uses for the "location" axis.

## Phase 2 — Scraper (`scrape.py` → `data/threads.jsonl`)

The forum is Fossil-powered. Threads render for anonymous users at
`/bugs/info/<hash>` (title, every post body, authors, timestamps, status).
The scraper enumerates all posts via `timeline.rss?y=f`, dedupes to unique
threads by root hash, and extracts referenced source files/functions. Pages are
cached under `data/raw/` so re-runs are instant and polite to sqlite.org.

## Phase 3 — Validity filter (in `classify.py`)

Status-driven, because on this forum `resolved` means the SQLite team confirmed
and fixed the report:

| verdict | rule |
|---|---|
| **invalid** | `status = not-planned`, or a meta/appreciation/policy post, or (only when status is unknown) an explicit developer "not a bug / works as designed / cannot reproduce" |
| **valid**   | everything else (`resolved`, `open`, or status-unknown defect reports) |

Near-duplicate clusters (same module + class + cited symbol) are *surfaced as
metadata*, not dropped — duplication is not invalidity.

## Phase 4 — Profiling & taxonomy (`out/`)

Each valid bug is profiled on two axes:

* **module** (location) — from cited file paths (strongest), else cited
  functions via `symbols.json`, else SQL-feature keywords. ~70% of bugs are
  attributed from an explicitly cited file/function.
* **bug-class** (type) — sanitizer fingerprints + symptom language, into
  families: `memory_safety` (buffer_overflow, null_deref, integer_overflow,
  use_after_free, stack_overflow, uninitialized), `correctness`
  (logic_wrong_result), `corruption`, `assertion`, `undefined_behavior`,
  `resource`, `crash`.

Outputs:

| file | contents |
|---|---|
| `data/bugs.jsonl` | one enriched record per thread (module, class, tags, sanitizers, validity, dup, refs) |
| `out/taxonomy.json` | totals, per-module / per-class / per-family / per-layer counts, the module×class matrix, duplicate clusters |
| `out/taxonomy.md` | human-readable report: class table, module table, the matrix, and per-cell bug lists with links |
| `out/adjacency.json` | per-bug index of adjacent bugs (`same_module_same_class`, `same_module`, `same_class`) to guide an agent |

## Using the taxonomy to steer an agent

Given a freshly found or known bug, look it up in `out/adjacency.json` by its
root hash: `same_module_same_class` lists the highest-signal neighbours (same
subsystem, same defect pattern). The dense matrix cells (e.g.
`ext_misc × buffer_overflow`, `optimizer × logic_wrong_result`) are the
subsystem/defect combinations most worth probing next.

## Caveats

* The corpus is a *dedicated bug forum* dominated by agent/fuzzer-found reports
  (memory-safety heavy); it is not the full historical SQLite ticket tracker
  (captcha-gated) nor the general user forum.
* Bug-class attribution is heuristic; ~9% land in `unknown` (niche build/CLI/API
  quirks) and are labelled honestly rather than force-fit. These are the natural
  candidates for a follow-up LLM profiling pass.

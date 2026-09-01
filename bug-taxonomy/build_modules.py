#!/usr/bin/env python3
"""
Phase 1 - Modularization.

Reads the SQLite source tree and assigns every core (`src/`) and extension
(`ext/`) source file to a conceptual subsystem *module*, grouped into
architectural *layers* following the canonical pipeline documented in
AGENTS.md / https://sqlite.org/arch.html:

    tokenizer -> parser -> code generator -> optimizer -> VDBE -> B-Tree
    -> Pager -> WAL -> VFS

plus the supporting subsystems (memory, mutex, utilities, public API) and the
loadable extensions under ext/.

Output: modules.json  -- the "location" axis of the bug taxonomy and the
file -> module resolver used by the classifier (Phase 4).

Regenerate with:  python3 build_modules.py --src ../sqlite
"""
import argparse
import fnmatch
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Module definitions.
#
# Each module: id, human name, layer, one-line description, and the list of
# glob patterns (relative to the repo root) whose files belong to it.  Order
# matters: the first module whose pattern matches a file wins, so more specific
# modules are listed before catch-alls (e.g. ext_misc_* before ext_misc).
# ---------------------------------------------------------------------------
MODULES = [
    # ---- Front end: SQL text -> parse tree ----
    dict(id="tokenizer", name="Tokenizer", layer="frontend",
         desc="Converts raw SQL text into tokens; input completeness checks.",
         patterns=["src/tokenize.c", "src/complete.c", "src/keywordhash.h"]),
    dict(id="parser", name="Parser / name resolution", layer="frontend",
         desc="Lemon grammar, parse-tree construction, name resolution and tree walking.",
         patterns=["src/parse.y", "src/parse.c", "src/parse.h", "src/resolve.c",
                   "src/walker.c", "src/treeview.c"]),

    # ---- Code generator: parse tree -> VDBE program ----
    dict(id="codegen_core", name="Code generator (DDL/misc)", layer="codegen",
         desc="Schema/DDL code generation and prepare glue: CREATE/ALTER/ANALYZE/VACUUM/ATTACH/pragma/auth.",
         patterns=["src/build.c", "src/alter.c", "src/analyze.c", "src/attach.c",
                   "src/auth.c", "src/vacuum.c", "src/pragma.c", "src/pragma.h",
                   "src/prepare.c", "src/callback.c", "src/table.c", "src/fkey.c"]),
    dict(id="codegen_dml", name="Code generator (DML)", layer="codegen",
         desc="Query and mutation code generation: SELECT, INSERT, UPDATE, DELETE, UPSERT, triggers.",
         patterns=["src/select.c", "src/insert.c", "src/update.c", "src/delete.c",
                   "src/upsert.c", "src/trigger.c"]),
    dict(id="expr", name="Expression engine", layer="codegen",
         desc="Expression parsing/analysis and expression code generation.",
         patterns=["src/expr.c"]),
    dict(id="window", name="Window functions", layer="codegen",
         desc="SQL window-function rewriting and code generation.",
         patterns=["src/window.c"]),

    # ---- Optimizer / query planner ----
    dict(id="optimizer", name="Query planner / optimizer", layer="optimizer",
         desc="WHERE-clause analysis, index selection, join ordering, query flattening.",
         patterns=["src/where.c", "src/wherecode.c", "src/whereexpr.c", "src/whereInt.h"]),

    # ---- Back end: virtual machine ----
    dict(id="vdbe", name="VDBE (bytecode engine)", layer="vdbe",
         desc="The virtual database engine: opcode interpreter, cursors, sorter, blob/vtab bridges, C API surface.",
         patterns=["src/vdbe.c", "src/vdbeapi.c", "src/vdbeaux.c", "src/vdbeblob.c",
                   "src/vdbemem.c", "src/vdbesort.c", "src/vdbetrace.c",
                   "src/vdbevtab.c", "src/vdbeInt.h", "src/vdbe.h"]),

    # ---- Virtual tables ----
    dict(id="vtab", name="Virtual table interface", layer="vtab",
         desc="Virtual-table machinery and built-in eponymous vtabs (dbpage, dbstat).",
         patterns=["src/vtab.c", "src/dbpage.c", "src/dbstat.c"]),

    # ---- Storage engine ----
    dict(id="btree", name="B-Tree", layer="storage",
         desc="On-disk B-tree: table/index storage, cursors, cell layout, balancing.",
         patterns=["src/btree.c", "src/btmutex.c", "src/btreeInt.h", "src/btree.h"]),
    dict(id="pager", name="Pager / journal", layer="storage",
         desc="Page cache management, transactions, rollback journal, backup, in-memory journal.",
         patterns=["src/pager.c", "src/pager.h", "src/backup.c", "src/memjournal.c"]),
    dict(id="wal", name="Write-Ahead Log", layer="storage",
         desc="WAL-mode transaction logging and checkpointing.",
         patterns=["src/wal.c", "src/wal.h"]),
    dict(id="pcache", name="Page cache", layer="storage",
         desc="Pluggable page-cache implementations.",
         patterns=["src/pcache.c", "src/pcache1.c", "src/pcache.h"]),

    # ---- OS / VFS layer ----
    dict(id="os_vfs", name="OS interface / VFS", layer="os",
         desc="Virtual File System abstraction and native backends (unix, win, in-memory KV).",
         patterns=["src/os.c", "src/os.h", "src/os_unix.c", "src/os_win.c",
                   "src/os_win.h", "src/os_kv.c", "src/os_common.h",
                   "src/os_setup.h", "src/memdb.c"]),

    # ---- Types, functions, text ----
    dict(id="json", name="JSON subsystem", layer="types_functions",
         desc="Built-in JSON / JSONB functions and virtual tables.",
         patterns=["src/json.c"]),
    dict(id="functions", name="Built-in functions", layer="types_functions",
         desc="Scalar/aggregate SQL functions, date-time functions, printf formatting.",
         patterns=["src/func.c", "src/date.c", "src/printf.c"]),
    dict(id="text_utf", name="Text / UTF handling", layer="types_functions",
         desc="UTF-8/16 conversion and collation-relevant text handling.",
         patterns=["src/utf.c"]),

    # ---- Memory management ----
    dict(id="memory", name="Memory allocation", layer="memory",
         desc="malloc wrappers, lookaside, alternative allocators (mem0..mem5), OOM/fault simulation.",
         patterns=["src/malloc.c", "src/mem0.c", "src/mem1.c", "src/mem2.c",
                   "src/mem3.c", "src/mem5.c", "src/fault.c", "src/status.c"]),

    # ---- Concurrency primitives ----
    dict(id="mutex", name="Mutex / threading", layer="util",
         desc="Mutex abstractions and thread helpers.",
         patterns=["src/mutex.c", "src/mutex.h", "src/mutex_noop.c",
                   "src/mutex_unix.c", "src/mutex_w32.c", "src/threads.c",
                   "src/notify.c"]),

    # ---- Core utilities / data structures ----
    dict(id="util", name="Core utilities", layer="util",
         desc="Shared helpers and data structures: util, hash, bitvec, rowset, random, globals.",
         patterns=["src/util.c", "src/hash.c", "src/hash.h", "src/bitvec.c",
                   "src/rowset.c", "src/random.c", "src/global.c",
                   "src/sqliteInt.h", "src/sqliteLimit.h", "src/hwtime.h",
                   "src/msvc.h", "src/vxworks.h"]),

    # ---- Public API / connection lifecycle ----
    dict(id="main_api", name="Public API / lifecycle", layer="api",
         desc="Connection open/close, C API entry points, legacy exec, extension loading.",
         patterns=["src/main.c", "src/legacy.c", "src/loadext.c",
                   "src/sqlite3ext.h", "src/sqlite.h.in", "src/carray.c"]),

    # ---- TCL / test glue (usually excluded but mapped for completeness) ----
    dict(id="tcl_glue", name="TCL bindings", layer="tooling",
         desc="TCL language bindings used by the test harness.",
         patterns=["src/tclsqlite.c", "src/tclsqlite.h"]),
    dict(id="cli", name="CLI shell", layer="tooling",
         desc="The sqlite3 command-line shell.",
         patterns=["src/shell.c.in", "src/shell.c"]),

    # ---- Extensions (ext/) ----
    dict(id="ext_fts5", name="FTS5 full-text search", layer="extension",
         desc="Full-Text Search version 5 (current).", patterns=["ext/fts5/*"]),
    dict(id="ext_fts3", name="FTS3/FTS4 full-text search", layer="extension",
         desc="Legacy full-text search (FTS3/FTS4).", patterns=["ext/fts3/*"]),
    dict(id="ext_rtree", name="R-Tree", layer="extension",
         desc="R-Tree spatial index and geopoly.", patterns=["ext/rtree/*"]),
    dict(id="ext_session", name="Session / changeset", layer="extension",
         desc="Session extension: changesets and patchsets.", patterns=["ext/session/*"]),
    dict(id="ext_rbu", name="RBU update", layer="extension",
         desc="Resumable Bulk Update.", patterns=["ext/rbu/*"]),
    dict(id="ext_recover", name="Recover", layer="extension",
         desc="Corrupt-database recovery API.", patterns=["ext/recover/*"]),
    dict(id="ext_expert", name="Expert / index advisor", layer="extension",
         desc="Index recommendation ('expert') tool.", patterns=["ext/expert/*"]),
    dict(id="ext_intck", name="Integrity check", layer="extension",
         desc="Incremental integrity-check extension.", patterns=["ext/intck/*"]),
    dict(id="ext_qrf", name="Query Result Formatter", layer="extension",
         desc="Query result formatting / EXPLAIN QUERY PLAN stats library.", patterns=["ext/qrf/*"]),
    dict(id="ext_icu", name="ICU", layer="extension",
         desc="ICU (Unicode) collation/case integration.", patterns=["ext/icu/*"]),
    dict(id="ext_jni", name="JNI bindings", layer="extension",
         desc="Java Native Interface bindings.", patterns=["ext/jni/*"]),
    dict(id="ext_wasm", name="WASM / JS", layer="extension",
         desc="WebAssembly and JavaScript build.", patterns=["ext/wasm/*"]),
    dict(id="ext_misc", name="Misc single-file extensions", layer="extension",
         desc="ext/misc/* utility extensions (compress, csv, series, amatch, etc.).",
         patterns=["ext/misc/*"]),
    dict(id="ext_other", name="Other extensions", layer="extension",
         desc="Any remaining ext/ file.", patterns=["ext/*"]),
]


def resolve(relpath, modules):
    """Return the id of the first module whose glob matches relpath."""
    for m in modules:
        for pat in m["patterns"]:
            if fnmatch.fnmatch(relpath, pat):
                return m["id"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="../sqlite", help="path to SQLite source tree")
    ap.add_argument("--out", default="modules.json")
    args = ap.parse_args()

    src_root = Path(args.src).resolve()
    if not (src_root / "src").is_dir():
        sys.exit(f"error: {src_root} does not look like a SQLite tree (no src/)")

    # Collect candidate source files under src/ and ext/.
    exts = {".c", ".h", ".y", ".in", ".java", ".js", ".c.in"}
    files = []
    for sub in ("src", "ext"):
        for p in (src_root / sub).rglob("*"):
            if p.is_file() and (p.suffix in exts or p.name.endswith(".c.in")):
                files.append(str(p.relative_to(src_root)))
    files.sort()

    file_to_module = {}
    unassigned = []
    for f in files:
        # Skip obvious test files in src/ (test1.c, test_*.c) - not shipped code.
        base = os.path.basename(f)
        if f.startswith("src/") and (base.startswith("test") and base[4:5] in ("_", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".")):
            continue
        mid = resolve(f, MODULES)
        if mid:
            file_to_module[f] = mid
        else:
            unassigned.append(f)

    module_to_files = {}
    for f, mid in file_to_module.items():
        module_to_files.setdefault(mid, []).append(f)

    # Layer ordering for presentation.
    layer_order = ["frontend", "codegen", "optimizer", "vdbe", "vtab",
                   "storage", "os", "types_functions", "memory", "util",
                   "api", "tooling", "extension"]

    modules_out = []
    for m in MODULES:
        fl = sorted(module_to_files.get(m["id"], []))
        modules_out.append({
            "id": m["id"], "name": m["name"], "layer": m["layer"],
            "description": m["desc"], "file_count": len(fl), "files": fl,
        })
    modules_out.sort(key=lambda m: (layer_order.index(m["layer"]), m["id"]))

    doc = {
        "sqlite_version": (src_root / "VERSION").read_text().strip()
            if (src_root / "VERSION").exists() else "unknown",
        "layer_order": layer_order,
        "module_count": len(modules_out),
        "assigned_file_count": len(file_to_module),
        "modules": modules_out,
        "file_to_module": dict(sorted(file_to_module.items())),
        "unassigned": sorted(unassigned),
    }
    Path(args.out).write_text(json.dumps(doc, indent=2))

    print(f"SQLite {doc['sqlite_version']}: {len(modules_out)} modules, "
          f"{len(file_to_module)} files assigned, {len(unassigned)} unassigned.")
    print(f"wrote {args.out}")
    if unassigned:
        print("\nUnassigned (first 20):")
        for u in unassigned[:20]:
            print("  ", u)


if __name__ == "__main__":
    main()

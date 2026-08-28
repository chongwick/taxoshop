# SQLite source module model

Conceptual modularization of [sqlite/sqlite](https://github.com/sqlite/sqlite). SQLite is a **modular monolith**: sharp internal layers and file-level ownership, compiled as one library (usually the `sqlite3.c` amalgamation).

Official architecture: [sqlite.org/arch.html](https://www.sqlite.org/arch.html)

```
Interface
    └── SQL Command Processor
            ├── Tokenizer → Parser → Code Generator   (SQL compiler)
            └── Virtual Machine (VDBE)
                    └── B-Tree
                            └── Pager / Page Cache / WAL
                                    └── OS Interface (VFS)
Utilities + Test Code cut across all of this.
```

Query data path:

`API → tokenize → parse → resolve → where/select codegen → Vdbe bytecode → btree cursor → pager page → VFS I/O`

Machine-readable companion: `sqlite-module-model.json`

---

## M0 — Public API and connection lifecycle

Owns the `sqlite3*` handle, prepare/step/finalize, config, and the C API surface. The only layer applications should call. Everything below is private and version-unstable.

| File | Role |
|---|---|
| `src/sqlite.h.in` → `sqlite3.h` | Public API template |
| `src/sqlite3ext.h` | Loadable-extension API |
| `src/sqliteInt.h`, `src/sqliteLimit.h` | Internal types, limits, shared structs |
| `src/main.c` | Open/close, init, most of `sqlite3_*` |
| `src/legacy.c` | Older API entry points |
| `src/prepare.c` | `sqlite3_prepare*` / statement compilation entry |
| `src/vdbeapi.c` | `sqlite3_step`, bind, column, reset |
| `src/complete.c` | `sqlite3_complete` |
| `src/table.c` | `sqlite3_get_table` |
| `src/callback.c` | Collation / function / busy-handler registration |
| `src/loadext.c` | Dynamic extension loading |
| `src/auth.c` | Authorizer |
| `src/status.c` | `sqlite3_status` / connection stats |
| `src/notify.c` | Unlock notify |
| `src/backup.c` | Online backup API |

Key types: `sqlite3`, `sqlite3_stmt`, `sqlite3_context`

Depends on: M1, M2, M6

---

## M1 — SQL compiler

Turns a string into a `Vdbe` program. Officially: Tokenizer + Parser + Code Generator.

### M1a — Lexer and parser

| File | Role |
|---|---|
| `src/tokenize.c` | Lexer (`sqlite3GetToken`) |
| `src/parse.y` | Lemon LALR(1) grammar → generated `parse.c` / `parse.h` |
| `keywordhash.h` | Generated keyword table |

Lemon lives in `tool/lemon.c` + `tool/lempar.c`, not in the library. `keywordhash.h` is produced by `tool/mkkeywordhash.c`.

### M1b — Name resolution, AST walk, schema DDL

| File | Role |
|---|---|
| `src/resolve.c` | Name resolution (`sqlite3ResolveExprNames`) |
| `src/walker.c` | Generic expression/SELECT tree walker |
| `src/treeview.c` | Debug dump of parse trees |
| `src/expr.c` | Expression analysis + codegen |
| `src/build.c` | CREATE/DROP and miscellaneous DDL |
| `src/alter.c` | ALTER TABLE |
| `src/analyze.c` | ANALYZE / stat tables |
| `src/attach.c` | ATTACH / DETACH |
| `src/vacuum.c` | VACUUM |
| `src/pragma.c` + generated `pragma.h` | PRAGMA dispatch |
| `src/trigger.c` | Triggers |
| `src/fkey.c` | Foreign keys |
| `src/vtab.c` | Virtual-table module registration and xBestIndex plumbing |

### M1c — DML and query planner

| File | Role |
|---|---|
| `src/select.c` | SELECT planning and codegen |
| `src/insert.c`, `src/upsert.c` | INSERT / UPSERT |
| `src/update.c`, `src/delete.c` | UPDATE / DELETE |
| `src/where.c`, `src/wherecode.c`, `src/whereexpr.c`, `src/whereInt.h` | Query planner / WHERE optimizer |
| `src/window.c` | Window functions |
| `src/rowset.c` | Row-set used by IN / DISTINCT / delete-of-self |

`where*` is the optimizer. It emits VDBE loops; it does not execute them.

Key types: `Parse`, `Select`, `Expr`, `WhereInfo`, `WhereLoop`

Depends on: M2, M6, M7

---

## M2 — VDBE bytecode virtual machine

SQL does not run directly. The compiler emits opcodes; `sqlite3VdbeExec()` interprets them. This is the clean cut between compile and execute. Cursors in the VM point at B-tree or virtual-table cursors.

| File | Role |
|---|---|
| `src/vdbe.c` | Interpreter: opcode switch |
| `src/vdbe.h` | VM API used by the rest of SQLite |
| `src/vdbeInt.h` | Private `Vdbe`, `VdbeOp`, `VdbeCursor` |
| `src/vdbeaux.c` | Opcode emission helpers + VM utilities |
| `src/vdbemem.c` | `Mem` values (typed VM registers) |
| `src/vdbeblob.c` | Incremental BLOB I/O |
| `src/vdbesort.c` | External sort |
| `src/vdbetrace.c` | `EXPLAIN` / tracing |
| `src/vdbevtab.c` | VM-facing virtual-table ops |
| generated `opcodes.h` / `opcodes.c` | Opcode numbers and names |

Tools: `tool/mkopcodeh.tcl`, `tool/mkopcodec.tcl`

Key types: `Vdbe`, `VdbeOp`, `VdbeCursor`, `Mem`

Depends on: M3, M6, M7

---

## M3 — B-tree storage engine

Tables and indexes as B-trees. Owns on-disk cell/page format together with pager page size.

| File | Role |
|---|---|
| `src/btree.c` | `Btree`, `BtShared`, `BtCursor` |
| `src/btree.h` | Interface used by VDBE / schema |
| `src/btreeInt.h` | Private page/cell format |
| `src/btmutex.c` | Shared-cache locking around `BtShared` |

Key types: `Btree`, `BtShared`, `BtCursor`, `MemPage`

Depends on: M4, M6

---

## M4 — Pager, page cache, and WAL

Transactions, commit/rollback, page cache, rollback journal and WAL. **ACID lives here**, not in the B-tree. B-tree asks the pager for pages; pager talks to VFS.

| File | Role |
|---|---|
| `src/pager.c`, `src/pager.h` | Page I/O, rollback journal, commit, locking |
| `src/wal.c`, `src/wal.h` | Write-Ahead Log mode |
| `src/pcache.c`, `src/pcache.h` | Page-cache interface |
| `src/pcache1.c` | Default in-process cache |
| `src/bitvec.c` | Bit vectors for journal page sets |
| `src/memjournal.c` | In-memory journal |

`backup.c` (listed under M0) uses pager internals for page-wise copy.

Key types: `Pager`, `PgHdr`, `PCache`, `Wal`

Depends on: M5, M6

---

## M5 — VFS / OS interface

Portable file and OS abstraction. Core never calls `read()` / `WriteFile` directly. New platforms plug in a `sqlite3_vfs` + `sqlite3_io_methods`.

| File | Role |
|---|---|
| `src/os.h`, `src/os.c` | VFS dispatcher |
| `src/os_common.h`, `src/os_setup.h` | Shared OS helpers |
| `src/os_unix.c` | POSIX VFS |
| `src/os_win.c`, `src/os_win.h` | Windows VFS |
| `src/os_kv.c` | Key-value / experimental VFS |
| `src/vxworks.h` | VxWorks bits |
| `src/memdb.c` | In-memory database as a VFS |

Key types: `sqlite3_vfs`, `sqlite3_file`, `sqlite3_io_methods`

Depends on: M6

---

## M6 — Runtime services

Used by every layer; not a feature module.

### M6a — Memory and concurrency

| File | Role |
|---|---|
| `src/malloc.c` | SQLite allocator wrapper |
| `src/mem0.c`–`src/mem5.c` | Pluggable allocators |
| `src/mutex.c`, `src/mutex.h` | Mutex interface |
| `src/mutex_noop.c`, `src/mutex_unix.c`, `src/mutex_w32.c` | Implementations |
| `src/threads.c` | Thread helpers |
| `src/fault.c` | Fault injection |

### M6b — Values, text, randomness

| File | Role |
|---|---|
| `src/util.c` | Strings, conversions, misc |
| `src/utf.c` | UTF-8 / UTF-16 |
| `src/printf.c` | `sqlite3_mprintf` and internal formatting |
| `src/hash.c`, `src/hash.h` | Hash tables |
| `src/random.c` | PRNG |
| `src/hwtime.h` | Cycle counter |
| `src/global.c` | Process-wide globals |
| `src/msvc.h` | MSVC compatibility |

Depends on: nothing

---

## M7 — Built-in SQL functions and core virtual tables

Callback implementations the VM and schema invoke. Not the compiler.

| File | Role |
|---|---|
| `src/func.c` | Core SQL functions and aggregates |
| `src/date.c` | Date/time functions |
| `src/json.c` | JSON1 (in-core) |
| `src/carray.c` | `carray` table-valued function |
| `src/dbpage.c` | `sqlite_dbpage` vtab |
| `src/dbstat.c` | `dbstat` vtab |

`window.c` also implements window-function runtime pieces (listed with M1c because it is primarily a compiler/planner file). Some functions (`typeof`, `coalesce`) are compiled straight to bytecode in M1 instead of calling `func.c`.

Depends on: M2, M6

---

## M8 — Optional extensions

Sit beside the core via the virtual-table and loadable-extension APIs (`vtab.c`, `loadext.c`, `sqlite3ext.h`). FTS/RTREE are the usual built-into-amalgamation set.

| Directory | Module | Often in amalgamation |
|---|---|---|
| `ext/fts3/` | FTS3/FTS4 full-text search | yes |
| `ext/fts5/` | FTS5 full-text search | yes |
| `ext/rtree/` | R-tree spatial index | yes |
| `ext/session/` | Session / changeset | no |
| `ext/rbu/` | Resumable bulk update | no |
| `ext/icu/` | ICU collation / regex | no |
| `ext/recover/` | Database recovery | no |
| `ext/expert/` | Index advisor | no |
| `ext/intck/` | Integrity cross-check | no |
| `ext/misc/` | One-file extensions (regexp, csv, series, …) | no (many CLI-only) |
| `ext/jni/` | JNI bindings | no |
| `ext/wasm/` | WebAssembly bindings | no |
| `ext/qrf/` | Query result formatter | no |

Depends on: M0, M7

---

## M9 — Shell, bindings, tests, and build plane

Not part of `libsqlite3`.

| Area | Files |
|---|---|
| CLI | `src/shell.c.in` → `shell.c` |
| Tcl binding | `src/tclsqlite.c`, `src/tclsqlite.h` |
| Windows resource | `src/sqlite3.rc` |
| In-tree test C | every `src/test*.c` → `testfixture` |
| Test scripts | `test/`, `mptest/` |
| Codegen tools | `tool/lemon.c`, `mksqlite3h.tcl`, `mksqlite3c.tcl`, `split-sqlite3c.tcl`, `mkopcodeh.tcl`, `mkopcodec.tcl`, `mkkeywordhash.c`, `mkpragmatab.tcl` |

Generated artifacts: `sqlite3.h`, `parse.c`, `parse.h`, `opcodes.h`, `opcodes.c`, `keywordhash.h`, `pragma.h`, amalgamation `sqlite3.c` (optionally split as `sqlite3-all.c` + `sqlite3-1.c` …).

The amalgamation is a **packaging** module, not an architectural one: `tool/mksqlite3c.tcl` concatenates M0–M7 so the compiler can inline across layer boundaries.

---

## Ownership diagram

```
┌─────────────────────────────────────────────────────────────┐
│  M0  Public API          main, prepare, vdbeapi, sqlite.h.in │
├─────────────────────────────────────────────────────────────┤
│  M1  SQL compiler                                            │
│      lex: tokenize          parse: parse.y                   │
│      resolve/walk: resolve, walker, expr                     │
│      statements: select, insert, update, delete, build, …    │
│      planner: where / wherecode / whereexpr                  │
├─────────────────────────────────────────────────────────────┤
│  M2  VDBE                vdbe, vdbeaux, vdbemem, vdbesort    │
├─────────────────────────────────────────────────────────────┤
│  M3  B-tree              btree, btmutex                      │
│  M4  Pager/WAL/cache     pager, wal, pcache, pcache1         │
│  M5  VFS                 os, os_unix, os_win, memdb          │
├─────────────────────────────────────────────────────────────┤
│  M6  Runtime services    malloc, mutex, util, utf, hash      │
│  M7  SQL builtins        func, date, json, window, vtabs     │
│  M8  Optional engines    ext/fts5, ext/rtree, ext/session…   │
└─────────────────────────────────────────────────────────────┘
         ▲
    M9 shell / tcl / tests / tool (outside the library)
```

---

## Hard vs soft boundaries

Real (stable internal headers):

| Header | From | To |
|---|---|---|
| `vdbe.h` | rest of core | M2 VDBE |
| `btree.h` | VM / schema | M3 B-tree |
| `pager.h` | B-tree | M4 pager |
| `os.h` / `sqlite3_vfs` | pager | M5 VFS |
| `pcache.h` | pager | page cache implementation |
| `sqlite3ext.h` | core | M8 loadable modules |

Soft (same `sqliteInt.h`, heavy sharing of `Parse` / `sqlite3`):

- Tokenizer, parser actions, and code generator
- `expr.c` ↔ `select.c` ↔ `where.c`
- Built-in functions vs code generator
- JSON / window / vtab code that straddles compiler and runtime

The design is layered for reasoning and testing, not for dynamic linkage. A stricter split for study would cut at M1–M5, with M6 as a required runtime crate and M8 behind the extension ABI. The amalgamation would remain the production artifact.

---

## Repo layout (not modules)

| Directory | Contents |
|---|---|
| `src/` | Primary core C; also `test*.c`, Tcl binding, shell |
| `ext/` | Optional extensions |
| `test/` | TCL scripts and extra test programs |
| `tool/` | Lemon, header/amalgamation generators, diagnostics |
| `doc/` | Internal docs (user docs are a separate repo) |
| `autoconf/` | Autotools / packaging |
| `contrib/` | Contributed extras |

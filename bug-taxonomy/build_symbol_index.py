#!/usr/bin/env python3
"""
Build a function/symbol -> module index from the SQLite source tree.

Used by the classifier (Phase 4) to attribute a bug to a module when the report
names a C function (e.g. `uncompressFunc`, `fts3ContentColumns`) rather than a
file path.  We scan every file assigned by build_modules.py, extract top-level
function definitions, and map each defined symbol to that file's module.

Output: symbols.json  { "func_name": "module_id", ... }

Regenerate:  python3 build_symbol_index.py --src ../sqlite
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

# Match C function definitions at start of line:  <type...> name( ...
# Deliberately conservative to avoid calls/prototypes; requires the name to be
# immediately followed by '(' and the line to look like a definition head.
DEF_RE = re.compile(
    r"^(?:[A-Za-z_][\w ]*?[\s*])([A-Za-z_][A-Za-z0-9_]+)\s*\([^;]*$",
    re.M,
)
# common keywords that are not function names
NOT_FUNC = {"if", "for", "while", "switch", "return", "sizeof", "do",
            "else", "typedef", "struct", "union", "enum", "static", "case"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="../sqlite")
    ap.add_argument("--modules", default="modules.json")
    ap.add_argument("--out", default="symbols.json")
    args = ap.parse_args()

    mods = json.load(open(args.modules))
    file_to_module = mods["file_to_module"]
    src_root = Path(args.src).resolve()

    sym_files = {}  # func -> Counter(module)
    for relpath, module in file_to_module.items():
        p = src_root / relpath
        if not p.exists() or p.suffix not in (".c",):
            continue
        try:
            text = p.read_text(errors="replace")
        except Exception:  # noqa: BLE001
            continue
        for m in DEF_RE.finditer(text):
            name = m.group(1)
            if name in NOT_FUNC or len(name) < 3:
                continue
            sym_files.setdefault(name, Counter())[module] += 1

    # Resolve each symbol to its dominant module.
    symbols = {name: c.most_common(1)[0][0] for name, c in sym_files.items()}
    Path(args.out).write_text(json.dumps(symbols, indent=0))
    print(f"indexed {len(symbols)} symbols across "
          f"{len(set(symbols.values()))} modules -> {args.out}")


if __name__ == "__main__":
    main()

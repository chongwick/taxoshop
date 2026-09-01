#!/usr/bin/env python3
"""
Phase 3 (validity filter) + Phase 4 (profiling / 2D taxonomy).

Input : data/threads.jsonl   (from scrape.py)
        modules.json          (from build_modules.py)
        symbols.json          (from build_symbol_index.py)

For each thread we:
  * decide VALIDITY  (real bug vs. not-planned / question / rejected)
  * attribute a MODULE (the "location" axis) from cited files, then functions,
    then SQL-feature keywords
  * attribute a BUG-CLASS (the "type" axis) from sanitizer signatures and
    symptom language, grouped into families
  * compute a dedupe signature and a short profile

Outputs:
  data/bugs.jsonl        one enriched record per thread
  out/taxonomy.json      the module x bug-class matrix + per-cell bug lists
  out/taxonomy.md        human-readable taxonomy report
  out/adjacency.json     per-bug "adjacent bugs" index to steer an agent

Usage:  python3 classify.py
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Bug-class taxonomy (the "type" axis).
# Ordered by precedence (first match wins for the *primary* class); every
# matching class is also recorded as a tag.  Each leaf maps to a family.
# ---------------------------------------------------------------------------
CLASS_RULES = [
    ("use_after_free", "memory_safety", [
        r"use[\s-]?after[\s-]?free", r"\bUAF\b", r"heap-use-after-free",
        r"double[\s-]?free", r"freed memory"]),
    ("buffer_overflow", "memory_safety", [
        r"heap-buffer-overflow", r"stack-buffer-overflow", r"global-buffer-overflow",
        r"buffer[\s-]?overflow", r"out[\s-]?of[\s-]?bounds", r"\bOOB\b",
        r"overread", r"overwrite", r"writes? past", r"reads? past",
        r"past the (?:end|buffer)", r"beyond the (?:end|buffer|allocation)"]),
    ("integer_overflow", "memory_safety", [
        r"integer overflow", r"\bint(?:eger)? overflow", r"signed integer overflow",
        r"size-header wrap", r"multiplication overflow", r"overflow(?:s|ed)? into",
        r"wrap(?:s|ped|ping)? (?:into|around|to)", r"\bi(?:nt)?64 overflow"]),
    ("null_deref", "memory_safety", [
        r"null[\s-]?pointer[\s-]?dereference", r"null[\s-]?deref",
        r"null dereference", r"unchecked[^.]{0,40}\bnull\b", r"\bnull\b[^.]{0,30}deref",
        r"dereferenc\w+ (?:a )?null", r"null (?:fed|passed|write|from|return)"]),
    ("uninitialized", "memory_safety", [
        r"uninitialized", r"use-of-uninitialized", r"\bMSan\b", r"uninit\b"]),
    ("stack_overflow", "memory_safety", [
        r"stack[\s-]?overflow", r"stack exhaustion", r"stack-buffer",
        r"(?:deep|infinite|unbounded) recursion", r"recursion depth"]),
    ("assertion_failure", "assertion", [
        r"assertion (?:failure|failed)", r"assert\s*\(", r"\bassert\b[^.]{0,20}fail",
        r"failed assert", r"SIGABRT.{0,30}assert"]),
    ("div_by_zero", "undefined_behavior", [
        r"division by zero", r"divide[\s-]?by[\s-]?zero", r"\bSIGFPE\b",
        r"floating point exception", r"modulo by zero"]),
    ("undefined_behavior", "undefined_behavior", [
        r"\bUBSan\b", r"undefined behaviou?r", r"misaligned", r"shift exponent",
        r"non-zero offset .* null", r"negation of", r"signed .* shift"]),
    ("memory_leak", "resource", [
        r"memory leak", r"\bleak(?:s|ed|ing)?\b", r"not freed", r"lsan"]),
    ("infinite_loop_hang", "resource", [
        r"infinite loop", r"does not terminate", r"never (?:returns|terminates)",
        r"\bhang(?:s|ing)?\b", r"endless loop", r"livelock"]),
    ("data_corruption", "corruption", [
        r"database (?:is )?corrupt", r"\bSQLITE_CORRUPT\b", r"corrupt(?:s|ed|ing|ion)\b",
        r"malformed database", r"wraps? .* to page 1", r"corrupt the (?:db|database|file)"]),
    ("logic_wrong_result", "correctness", [
        r"incorrect result", r"wrong result", r"unexpected result",
        r"different (?:result|subtype|row order|order)", r"inconsistent",
        r"returns? incorrect", r"wrong (?:answer|output|value|type)",
        r"should (?:return|be|produce|have been)", r"incorrect (?:output|value|type|behaviou?r)",
        r"unexpected (?:output|result|behaviou?r)", r"drops? (?:valid )?rows?",
        r"silently (?:truncat|ignor|discard|retain|los|drop)",
        r"\bbypass(?:es|ed|ing)?\b", r"zeroe?s\b", r"off[\s-]?by[\s-]?one",
        r"returns? empty", r"empty (?:set|result)", r"loses? the", r"discards?\b",
        r"truncat(?:e|es|ed|ing)", r"not eliminated", r"prunes nothing",
        r"invalid (?:complementary|result)", r"can be bypassed", r"evaluates? to (?:false|true)",
        r"returns? null", r"becomes? (?:an? )?(?:integer|zero|null)",
        r"only (?:removes?|applies|drops?) one", r"loses? .{0,20}collation",
        r"backward[\s-]?incompatible", r"retains?\b", r"constructs? invalid",
        r"inconsistent(?:ly)?\b", r"not (?:eliminated|applied|honou?red)"]),
    ("crash_generic", "crash", [
        r"\bSIGSEGV\b", r"\bSIGBUS\b", r"segfault", r"segmentation fault",
        r"\bcrash(?:es|ed|ing)?\b", r"\babort(?:s|ed|ing)?\b", r"\bSIGABRT\b"]),
]
CLASS_RE = [(name, fam, re.compile("|".join(pats), re.I)) for name, fam, pats in CLASS_RULES]

# Sanitizer fingerprints (secondary signal / metadata).
SANITIZERS = {
    "asan": re.compile(r"\bASan\b|AddressSanitizer|heap-buffer-overflow|heap-use-after-free", re.I),
    "ubsan": re.compile(r"\bUBSan\b|UndefinedBehaviorSanitizer|runtime error:", re.I),
    "msan": re.compile(r"\bMSan\b|MemorySanitizer|use-of-uninitialized", re.I),
    "valgrind": re.compile(r"valgrind|Invalid read|Invalid write", re.I),
}

# SQL-feature -> module keyword fallback (when no file/func is cited).
FEATURE_MODULE = [
    (r"\bwindow function|\bover\s*\(|row_number|rank\(\)|partition by", "window"),
    (r"\bjsonb?\b|json_|->>|json object|json array", "json"),
    (r"\bfts5\b|full-?text.*5", "ext_fts5"),
    (r"\bfts3\b|\bfts4\b|full-?text", "ext_fts3"),
    (r"\br-?tree\b|rtree|geopoly", "ext_rtree"),
    (r"\bchangeset|patchset|session extension|sqlite3session", "ext_session"),
    (r"\brecover\b|corrupt(?:ed)? database recover", "ext_recover"),
    (r"\brbu\b|resumable bulk", "ext_rbu"),
    (r"\bformat\s*\(|printf|strftime|\bdate\s*\(|\btime\s*\(|julianday", "functions"),
    (r"\bvacuum\b", "codegen_core"),
    (r"\bpragma\b", "codegen_core"),
    (r"\btrigger\b", "codegen_dml"),
    (r"\bupsert|on conflict", "codegen_dml"),
    (r"\bwhere\b.*\bindex\b|query plan|optimiz|\bbloom filter\b|\bDESC index\b", "optimizer"),
    (r"right join|left join|outer join|natural join|cross join|\bon clause\b", "optimizer"),
    (r"\bvirtual table|create virtual|shadow table", "vtab"),
    (r"\bwal\b|write-ahead", "wal"),
    (r"\bcollat", "text_utf"),
    (r"having\b|group by|\bdistinct\b|order by", "codegen_dml"),
    (r"correlated|scalar subquer|\bsubquer|\bCTE\b|common table expression", "codegen_dml"),
    (r"row-?value|\bIN\s*\(|\bnot in\b|\bIN predicate", "expr"),
    (r"\baffinity\b|\bcast\b|numeric|rowid.*(?:float|compar)", "expr"),
    (r"alter table", "codegen_core"),
    (r"autosetup|tclconfig|tclConfig|configure|testsuite|\bBSD\b|Makefile|build", "build"),
    (r"\bcommand-?line|\bshell\b|\bCLI\b|\.dump|\.import|\.mode|\.prompt", "cli"),
    (r"\bjoin\b", "optimizer"),
]
FEATURE_MODULE = [(re.compile(p, re.I), m) for p, m in FEATURE_MODULE]

# Explicit not-a-bug verdicts (anchored, conservative - used only when status
# is unknown, to avoid matching "invalid JSON" etc. inside bug descriptions).
EXPLICIT_REJECT_RE = re.compile(
    r"\bthis is not a bug\b|\bnot a bug\b|works? as (?:designed|intended)|"
    r"\bworking as intended\b|\bby design\b|cannot reproduce|can't reproduce|"
    r"unable to reproduce|\bwon'?t fix\b|\bnot planned\b|\buser error\b",
    re.I)
# Signs a thread is a question / feature request rather than a defect.
QUESTION_RE = re.compile(
    r"^\s*(?:how (?:do|can|to)|is (?:it|there)|why does|can (?:i|we|you)|"
    r"feature request|proposal|suggestion|question:)", re.I)
# Meta / policy / appreciation posts that are not defect reports.
META_RE = re.compile(
    r"^\s*meta:|^\s*re:|thank you|^\s*are .{0,60}in scope|^\s*policy\b|"
    r"^\s*announce", re.I)

# SQLite core developers (replies from them confirm/reject).
DEVS = {"drh", "dan", "stephan", "larrybr", "mistachkin"}


def classify_bug(text):
    tags, primary, fam = [], None, None
    for name, family, rx in CLASS_RE:
        if rx.search(text):
            tags.append(name)
            if primary is None:
                primary, fam = name, family
    if primary is None:
        primary, fam = "unknown", "other"
    sans = [s for s, rx in SANITIZERS.items() if rx.search(text)]
    return primary, fam, tags, sans


# File/function reference extraction (also applied to titles, which the
# scraper's body-only pass misses).
FILE_RE = re.compile(
    r"\b((?:src|ext)/[A-Za-z0-9_./-]+?\.(?:c|h|y|in)|[A-Za-z0-9_]+\.(?:c|h))\b")
FUNC_RE = re.compile(r"`?\b([A-Za-z_][A-Za-z0-9_]{2,})\(\)`?")


def attribute_module(th, file_to_module, symbols):
    votes = Counter()
    src = None
    # Merge references cited anywhere (title + body), not just body.
    text = th.get("_text", "")
    ref_files = sorted(set(th.get("referenced_files", [])) | set(FILE_RE.findall(text)))
    ref_funcs = sorted(set(th.get("referenced_funcs", [])) | set(FUNC_RE.findall(text)))
    th["referenced_files"] = ref_files
    th["referenced_funcs"] = ref_funcs
    # 1. cited file paths (strongest)
    for f in ref_files:
        m = file_to_module.get(f)
        if not m:  # try basename match
            base = f.split("/")[-1]
            for path, mod in file_to_module.items():
                if path.split("/")[-1] == base:
                    m = mod
                    break
        if m:
            votes[m] += 3
    if votes:
        src = "file"
    # 2. cited functions
    for fn in ref_funcs:
        m = symbols.get(fn)
        if m:
            votes[m] += 2
    if votes and src is None:
        src = "func"
    # 3. SQL-feature keywords
    if not votes:
        text = th.get("_text", "")
        for rx, mod in FEATURE_MODULE:
            if rx.search(text):
                votes[mod] += 1
        if votes:
            src = "feature"
    if not votes:
        return "unattributed", "unknown", "none"
    module = votes.most_common(1)[0][0]
    return module, src, dict(votes)


def decide_validity(th):
    """Validity is status-driven.  On this forum `resolved` means the SQLite
    team confirmed and fixed the report, so it is a real bug; `not-planned` is
    the won't-fix / not-a-defect bucket.  We only fall back to text heuristics
    when the status is missing, and even then require an *explicit* developer
    verdict (anchored phrases) - substrings like "invalid JSON" in a bug
    description must NOT count as a rejection."""
    status = th.get("status", "unknown")
    title = th.get("title", "") or ""
    if META_RE.search(title):
        return False, "meta-or-non-defect-post"
    if status == "not-planned":
        return False, "status:not-planned"
    if status == "resolved":
        return True, "confirmed"
    if status == "open":
        return True, "open-unconfirmed"
    # status unknown (title didn't match listing): apply conservative checks
    if QUESTION_RE.search(title):
        return False, "question-or-feature-request"
    dev_text = " ".join(p["body"] for p in th.get("posts", [])
                        if (p.get("author") or "").lower() in DEVS)
    if dev_text and EXPLICIT_REJECT_RE.search(dev_text):
        return False, "developer-rejected"
    return True, "status-unknown-assumed-valid"


def main():
    mods = json.load(open("modules.json"))
    file_to_module = mods["file_to_module"]
    module_meta = {m["id"]: m for m in mods["modules"]}
    # synthetic modules referenced only via feature keywords (no shipped .c file)
    module_meta.setdefault("build", {"id": "build", "name": "Build system",
                                     "layer": "tooling"})
    symbols = json.load(open("symbols.json"))
    threads = [json.loads(l) for l in open("data/threads.jsonl")]

    bugs = []
    skipped = 0
    for th in threads:
        # Skip non-thread artifacts (e.g. "Attachment Details" pages that RSS
        # surfaces for reproducer files) - they have no posts / no root hash.
        if not th.get("root_hash") or th.get("n_posts", 0) == 0:
            skipped += 1
            continue
        th["_text"] = ((th.get("title") or "") + "\n" +
                       "\n".join(p["body"] for p in th.get("posts", [])))
        valid, reason = decide_validity(th)
        primary, fam, tags, sans = classify_bug(th["_text"])
        module, msrc, votes = attribute_module(th, file_to_module, symbols)
        layer = module_meta.get(module, {}).get("layer", "unknown")
        rec = {
            "root_hash": th["root_hash"],
            "url": th.get("url"),
            "title": th.get("title"),
            "status": th.get("status"),
            "valid": valid,
            "validity_reason": reason,
            "module": module,
            "module_layer": layer,
            "module_source": msrc,
            "bug_class": primary,
            "bug_family": fam,
            "class_tags": tags,
            "sanitizers": sans,
            "reporter": th.get("reporter"),
            "n_posts": th.get("n_posts"),
            "first_ts": th.get("first_ts"),
            "referenced_files": th.get("referenced_files", []),
            "referenced_funcs": th.get("referenced_funcs", [])[:12],
        }
        # near-duplicate signature: only meaningful with a concrete code anchor
        # (a cited function or file).  Bugs without one get a unique signature so
        # unrelated logic bugs are never merged.
        anchor = (th.get("referenced_funcs") or th.get("referenced_files") or [None])[0]
        rec["dup_sig"] = (f"{module}|{primary}|{anchor}" if anchor
                          else f"__uniq__:{th['root_hash']}")
        rec["duplicate_of"] = None
        bugs.append(rec)

    # Surface near-duplicate clusters as metadata (do NOT drop them - duplicates
    # are not "invalid"; the taxonomy counts every valid bug).
    clusters = defaultdict(list)
    for b in bugs:
        if b["valid"] and not b["dup_sig"].startswith("__uniq__"):
            clusters[b["dup_sig"]].append(b["root_hash"])
    dup_clusters = {sig: hs for sig, hs in clusters.items() if len(hs) > 1}
    dup_members = {h for hs in dup_clusters.values() for h in hs[1:]}
    for b in bugs:
        if b["root_hash"] in dup_members:
            # point to the cluster representative (first seen)
            b["duplicate_of"] = clusters[b["dup_sig"]][0]

    valids = [b for b in bugs if b["valid"]]

    # ---- 2D taxonomy matrix: module x bug_class ----
    matrix = defaultdict(lambda: defaultdict(list))
    for b in valids:
        matrix[b["module"]][b["bug_class"]].append(b["root_hash"])

    taxonomy = {
        "sqlite_version": mods["sqlite_version"],
        "totals": {
            "threads": len(bugs),
            "valid_bugs": len(valids),
            "invalid": sum(1 for b in bugs if not b["valid"]),
            "near_duplicate_clusters": len(dup_clusters),
            "bugs_in_dup_clusters": sum(len(hs) for hs in dup_clusters.values()),
        },
        "duplicate_clusters": dup_clusters,
        "by_module": {m: sum(len(v) for v in cls.values())
                      for m, cls in matrix.items()},
        "by_class": dict(Counter(b["bug_class"] for b in valids)),
        "by_family": dict(Counter(b["bug_family"] for b in valids)),
        "by_layer": dict(Counter(b["module_layer"] for b in valids)),
        "matrix": {m: {c: hs for c, hs in cls.items()} for m, cls in matrix.items()},
    }

    # ---- adjacency: for each valid bug, sibling bugs in same module / class ----
    by_mod = defaultdict(list)
    by_cls = defaultdict(list)
    for b in valids:
        by_mod[b["module"]].append(b["root_hash"])
        by_cls[b["bug_class"]].append(b["root_hash"])
    idx = {b["root_hash"]: b for b in valids}
    adjacency = {}
    for b in valids:
        same_mod = [h for h in by_mod[b["module"]] if h != b["root_hash"]]
        same_cls = [h for h in by_cls[b["bug_class"]] if h != b["root_hash"]]
        adjacency[b["root_hash"]] = {
            "title": b["title"],
            "module": b["module"], "bug_class": b["bug_class"],
            "same_module_same_class": [h for h in same_mod if h in set(same_cls)],
            "same_module": same_mod[:25],
            "same_class": same_cls[:25],
        }

    Path("out").mkdir(exist_ok=True)
    with open("data/bugs.jsonl", "w") as f:
        for b in bugs:
            b.pop("_text", None)
            f.write(json.dumps(b) + "\n")
    json.dump(taxonomy, open("out/taxonomy.json", "w"), indent=2)
    json.dump(adjacency, open("out/adjacency.json", "w"), indent=2)
    write_markdown(taxonomy, valids, module_meta, idx)

    t = taxonomy["totals"]
    print(f"threads={t['threads']} valid={t['valid_bugs']} "
          f"invalid={t['invalid']} dup_clusters={t['near_duplicate_clusters']} "
          f"(skipped {skipped} non-thread artifacts)")
    print("by_family:", taxonomy["by_family"])
    print("top modules:", dict(Counter(taxonomy["by_module"]).most_common(8)))
    print("wrote out/taxonomy.json, out/taxonomy.md, out/adjacency.json, data/bugs.jsonl")


def write_markdown(tax, valids, module_meta, idx):
    lines = []
    A = lines.append
    A(f"# SQLite Bug Taxonomy (v{tax['sqlite_version']})\n")
    t = tax["totals"]
    A(f"Corpus: **{t['threads']}** forum threads -> "
      f"**{t['valid_bugs']}** valid bugs "
      f"({t['invalid']} filtered invalid; {t['near_duplicate_clusters']} "
      f"near-duplicate clusters covering {t['bugs_in_dup_clusters']} bugs).\n")

    A("\n## Bug classes (type axis)\n")
    A("| family | class | count |")
    A("|---|---|---:|")
    fam_of = {name: fam for name, fam, _ in CLASS_RULES}
    fam_of["unknown"] = "other"
    for cls, n in sorted(tax["by_class"].items(), key=lambda x: -x[1]):
        A(f"| {fam_of.get(cls,'?')} | `{cls}` | {n} |")

    A("\n## Modules (location axis)\n")
    A("| layer | module | bugs |")
    A("|---|---|---:|")
    for m, n in sorted(tax["by_module"].items(), key=lambda x: -x[1]):
        layer = module_meta.get(m, {}).get("layer", "?")
        A(f"| {layer} | `{m}` | {n} |")

    A("\n## Module x bug-class matrix\n")
    classes = [c for c, _ in sorted(tax["by_class"].items(), key=lambda x: -x[1])]
    header = "| module \\ class | " + " | ".join(f"`{c}`" for c in classes) + " | **tot** |"
    A(header)
    A("|" + "---|" * (len(classes) + 2))
    for m, n in sorted(tax["by_module"].items(), key=lambda x: -x[1]):
        row = tax["matrix"].get(m, {})
        cells = " | ".join(str(len(row.get(c, []))) or "" for c in classes)
        A(f"| `{m}` | {cells} | **{n}** |")

    A("\n## Per-cell bug lists\n")
    for m, n in sorted(tax["by_module"].items(), key=lambda x: -x[1]):
        A(f"\n### {m} ({n})\n")
        for cls, hs in sorted(tax["matrix"][m].items(), key=lambda x: -len(x[1])):
            A(f"- **{cls}** ({len(hs)}):")
            for h in hs:
                b = idx[h]
                A(f"  - [{b['title']}]({b['url']})")
    Path("out/taxonomy.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()

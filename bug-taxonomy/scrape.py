#!/usr/bin/env python3
"""
Phase 2 - Scraper for the SQLite Bug Forum (https://sqlite.org/bugs/forum).

The forum is Fossil-powered.  Individual threads render for anonymous users at
    https://sqlite.org/bugs/info/<artifact-hash>
showing the whole thread: every post's body, author, timestamp, and a
`data-fpid="<hash>"` on each post element.  The post whose block also contains
the thread `<h1>` title is the thread root; we dedupe threads by that root hash.

Thread *status* (Open / Resolved / Not Planned) is NOT on the post page - it
lives on the listing rows at /bugs/forum, so we scrape that separately and join
on the (normalized) title.

Pipeline:
  1. listing:  /bugs/forum?n=<big>            -> {norm_title: status, counts}
  2. enumerate: timeline.rss?y=f&n=<big>      -> all post hashes (chronological)
  3. for each unseen hash: GET /bugs/info/<hash>, parse the thread, mark all
     member fpids seen (so each thread is fetched once).

Politeness: on-disk HTML cache (data/raw/), configurable delay, custom UA.
Resumable: cached pages are reused; re-run any time.

Output: data/threads.jsonl  (one JSON object per unique thread)

Usage:
    python3 scrape.py                 # full run
    python3 scrape.py --limit 10      # smoke test (first 10 threads)
    python3 scrape.py --delay 1.0
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://sqlite.org/bugs"
UA = "sqlite-bug-taxonomy-research/1.0 (academic bug-taxonomy study; contact donkeychong99@gmail.com)"
RAW = Path("data/raw")
DATA = Path("data")


# ---------------------------------------------------------------------------
# HTTP with on-disk cache
# ---------------------------------------------------------------------------
def fetch(url, cache_path=None, delay=0.7):
    """GET url, caching to cache_path.  Returns text."""
    if cache_path and cache_path.exists():
        return cache_path.read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode("utf-8", errors="replace")
            break
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                raise
            sys.stderr.write(f"  retry {url}: {e}\n")
            time.sleep(2 * (attempt + 1))
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(body, encoding="utf-8")
    time.sleep(delay)  # be polite to sqlite.org
    return body


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"[ \t]*\n[ \t]*")


def strip_tags(s):
    s = re.sub(r"(?is)<script.*?</script>", " ", s)
    s = re.sub(r"(?is)<style.*?</style>", " ", s)
    s = TAG_RE.sub("", s)
    s = html.unescape(s)
    s = WS_RE.sub("\n", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def norm_title(t):
    t = html.unescape(t)
    t = TAG_RE.sub("", t)
    return re.sub(r"\s+", " ", t).strip().lower()


# ---------------------------------------------------------------------------
# 1. Listing -> status map
# ---------------------------------------------------------------------------
ROW_RE = re.compile(
    r'<tr data-status="([^"]*)"><td>([^<]*)</td>\s*'
    r"<td class='subject'>(.*?)</td>"
    r"<td>([^<]*)</td><td class='status'>([^<]*)</td>",
    re.S,
)


def scrape_listing(delay):
    htmltext = fetch(f"{BASE}/forum?n=5000&x=0", RAW / "listing.html", delay)
    out = {}
    for status, age, subject, counts, status_label in ROW_RE.findall(htmltext):
        title = re.sub(r"</?a[^>]*>", "", subject).strip()
        out[norm_title(title)] = {
            "status": status,
            "status_label": status_label.strip(),
            "age": age.strip(),
            "counts": counts.strip(),
            "title": html.unescape(title),
        }
    return out


# ---------------------------------------------------------------------------
# 2. Enumerate all post hashes (chronological, oldest last)
# ---------------------------------------------------------------------------
def enumerate_posts(delay):
    rss = fetch(f"https://sqlite.org/bugs/timeline.rss?y=f&n=5000",
                RAW / "timeline.rss", delay)
    items = re.findall(r"<item>(.*?)</item>", rss, re.S)
    posts = []
    for it in items:
        link = re.search(r"<link>([^<]+)</link>", it)
        title = re.search(r"<title>(.*?)</title>", it, re.S)
        pub = re.search(r"<pubDate>([^<]+)</pubDate>", it)
        creator = re.search(r"<dc:creator>([^<]*)</dc:creator>", it)
        if not link:
            continue
        m = re.search(r"/info/([a-f0-9]{40,})", link.group(1))
        if not m:
            continue
        raw_title = title.group(1).strip() if title else ""
        posts.append({
            "hash": m.group(1),
            "title": html.unescape(re.sub(r"^Reply:\s*", "", raw_title)).strip(),
            "is_reply": raw_title.startswith("Reply:"),
            "pubdate": pub.group(1).strip() if pub else None,
            "creator": creator.group(1).strip() if creator else None,
        })
    return posts  # newest first, as RSS delivers


# ---------------------------------------------------------------------------
# 3. Parse a thread info page
# ---------------------------------------------------------------------------
FPID_SPLIT = re.compile(r'data-fpid="([a-f0-9]{40,})"')
HDR_RE = re.compile(r"forumPostHdr'>\((\d+)\)(.*?)</h3>", re.S)
TS_RE = re.compile(r'data-content="([0-9T:\-Z]+)"')
AUTHOR_RE = re.compile(r"By\s+(.*?)\s+on\s", re.S)
BODY_RE = re.compile(r"<div class='forumPostBody'>(.*?)</div>\s*(?:</div>|<div class=\"forumpost)", re.S)

# Source-file references we care about for module attribution.
FILE_RE = re.compile(
    r"\b((?:src|ext)/[A-Za-z0-9_./-]+?\.(?:c|h|y|in)|[A-Za-z0-9_]+\.(?:c|h))\b"
)
FUNC_RE = re.compile(r"`?\b([A-Za-z_][A-Za-z0-9_]*)\(\)`?")


def parse_thread(page):
    # Split the page into post segments by data-fpid.
    parts = FPID_SPLIT.split(page)
    # parts = [prefix, fpid0, seg0, fpid1, seg1, ...]
    posts = []
    root_hash = None
    title = None
    for i in range(1, len(parts), 2):
        fpid = parts[i]
        seg = parts[i + 1]
        is_root = "<h1>" in seg[:200]
        if is_root:
            root_hash = fpid
            h1 = re.search(r"<h1>(.*?)</h1>", seg, re.S)
            if h1:
                title = strip_tags(h1.group(1))
        hdr = HDR_RE.search(seg)
        num = int(hdr.group(1)) if hdr else None
        hdrtxt = hdr.group(2) if hdr else seg[:400]
        ts = TS_RE.search(hdrtxt)
        author = AUTHOR_RE.search(strip_tags(hdrtxt))
        body_m = BODY_RE.search(seg)
        body = strip_tags(body_m.group(1)) if body_m else ""
        posts.append({
            "hash": fpid,
            "num": num,
            "author": author.group(1).strip() if author else None,
            "timestamp": ts.group(1) if ts else None,
            "body": body,
        })
    posts.sort(key=lambda p: (p["num"] is None, p["num"] or 0))
    fulltext = "\n".join(p["body"] for p in posts)
    files = sorted(set(FILE_RE.findall(fulltext)))
    funcs = sorted(set(FUNC_RE.findall(fulltext)))
    return {
        "root_hash": root_hash or (posts[0]["hash"] if posts else None),
        "title": title,
        "member_hashes": [p["hash"] for p in posts],
        "n_posts": len(posts),
        "reporter": posts[0]["author"] if posts else None,
        "first_ts": posts[0]["timestamp"] if posts else None,
        "last_ts": posts[-1]["timestamp"] if posts else None,
        "authors": sorted({p["author"] for p in posts if p["author"]}),
        "referenced_files": files,
        "referenced_funcs": funcs,
        "posts": posts,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay", type=float, default=0.7)
    ap.add_argument("--limit", type=int, default=0, help="max threads (0=all)")
    ap.add_argument("--out", default="data/threads.jsonl")
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)

    print("[1/3] scraping listing (status map)...")
    listing = scrape_listing(args.delay)
    print(f"      {len(listing)} threads in listing")

    print("[2/3] enumerating posts from RSS...")
    posts = enumerate_posts(args.delay)
    print(f"      {len(posts)} posts, {sum(1 for p in posts if not p['is_reply'])} root candidates")

    print("[3/3] fetching + parsing threads...")
    seen = set()
    threads = {}
    fetched = 0
    # oldest-first so thread numbering/root detection is stable
    for p in reversed(posts):
        if p["hash"] in seen:
            continue
        page = fetch(f"{BASE}/info/{p['hash']}", RAW / f"{p['hash']}.html", args.delay)
        fetched += 1
        th = parse_thread(page)
        for h in th["member_hashes"]:
            seen.add(h)
        key = th["root_hash"]
        if key in threads:
            continue
        # join status from listing by title
        meta = listing.get(norm_title(th["title"] or p["title"])) or {}
        th["status"] = meta.get("status", "unknown")
        th["status_label"] = meta.get("status_label", "")
        th["listing_counts"] = meta.get("counts", "")
        th["rss_reporter"] = p["creator"]
        th["url"] = f"{BASE}/info/{key}"
        threads[key] = th
        if fetched % 25 == 0:
            print(f"      fetched {fetched}, unique threads {len(threads)}")
        if args.limit and len(threads) >= args.limit:
            break

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        for th in threads.values():
            f.write(json.dumps(th) + "\n")

    # coverage report
    matched = sum(1 for t in threads.values() if t["status"] != "unknown")
    print(f"\ndone: {len(threads)} unique threads written to {args.out}")
    print(f"      status matched from listing: {matched}/{len(threads)}")
    import collections
    print("      status dist:",
          dict(collections.Counter(t["status"] for t in threads.values())))


if __name__ == "__main__":
    main()

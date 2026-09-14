#!/usr/bin/env python3
"""Scrape CRuby Bug reports from Ruby's Redmine tracker and render reports.

The authoritative source is https://bugs.ruby-lang.org/projects/ruby-master,
not GitHub. Run with no flags to collect the seed sanitizer candidates, cache
their raw Redmine pages, and render only those with an explicit PoC. Use
--discover to crawl the complete Bug tracker, then --all-candidates to process
that discovered list instead.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import html
import json
import re
import subprocess
import time
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BASE_URL = "https://bugs.ruby-lang.org"
ISSUES_URL = f"{BASE_URL}/projects/ruby-master/issues"
REPORTS = ROOT / "taxos" / "ruby_micro_taxo"
SOURCES = REPORTS / "sources"
RAW = SOURCES / "raw"
INDEX = SOURCES / "issues.json"
CANDIDATES = ROOT / "taxos" / "ruby_sanitizer_candidates.json"
PUBLIC_BUG_ID = re.compile(r'<tr\s+id="issue-(\d+)"[^>]*\btracker-1\b', re.I)
TITLE = re.compile(r"<title>Bug\s+#\d+:\s*(.*?)\s+-\s+Ruby\s+-\s+Ruby Issue Tracking System</title>", re.I | re.S)
DIAGNOSTIC = re.compile(r"(?:Address|Leak|Memory|Thread|UndefinedBehavior)Sanitizer|runtime error:|==\d+==|Invalid (?:read|write|free)|HEAP SUMMARY|ERROR SUMMARY", re.I)
POC_MARKER = re.compile(r"\b(?:poc|proof of concept|reproducer|reproduce|reproduction|steps to reproduce|minimal (?:script|example))\b", re.I)
CODE_BLOCK = re.compile(r"<(?:pre|code)[^>]*>(.*?)</(?:pre|code)>", re.I | re.S)
CODE_SIGNAL = re.compile(r"(?:\bruby\b|\.rb\b|\brequire\b|\bdef\b|\bclass\b|\bputs\b|#include\b|\bint\s+main\b)", re.I)
SOURCE_ATTACHMENT = re.compile(r"/attachments/[^\"'< >]+\.(?:rb|c|cc|cpp|h|py|sh)(?:[?#\"'< >]|$)", re.I)


class TextExtractor(HTMLParser):
    """Turn Redmine HTML into readable text without executing page content."""

    BLOCKS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "pre"}

    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip += 1
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip -= 1
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def text(self):
        return "\n".join(line.rstrip() for line in "".join(self.parts).splitlines() if line.strip())


def fetch(url):
    result = subprocess.run(
        ["curl", "--fail", "--silent", "--show-error", "--location", "--max-time", "90", url],
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def text_from_html(raw):
    parser = TextExtractor()
    parser.feed(raw.decode("utf-8", errors="replace"))
    return parser.text()


def discover(max_pages):
    """Return unique Bug tracker issue IDs from the paginated project list."""
    numbers, seen, page = [], set(), 1
    while max_pages is None or page <= max_pages:
        raw = fetch(f"{ISSUES_URL}?page={page}").decode("utf-8", errors="replace")
        added = [int(number) for number in PUBLIC_BUG_ID.findall(raw) if int(number) not in seen]
        if not added:
            break
        numbers.extend(added)
        seen.update(added)
        print(f"page {page}: {len(added)} issue IDs", flush=True)
        if "Next »" not in html.unescape(raw):
            break
        page += 1
        time.sleep(0.2)
    SOURCES.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps({"source": ISSUES_URL, "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "issues": numbers}, indent=2) + "\n")
    return numbers


def issue_numbers(max_pages):
    return discover(max_pages) if max_pages is not None or not INDEX.exists() else json.loads(INDEX.read_text())["issues"]


def candidate_numbers():
    """Load the sanitizer leads supplied for corpus verification."""
    return [record["number"] for record in json.loads(CANDIDATES.read_text())["issues"]]


def collect_issue(number):
    path = RAW / f"ruby_{number}.html"
    if path.exists():
        return number, "cached"
    raw = fetch(f"{BASE_URL}/issues/{number}")
    path.write_bytes(raw)
    return number, f"{len(raw)} bytes"


def collect_sources(numbers):
    RAW.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(collect_issue, number): number for number in numbers}
        for future in concurrent.futures.as_completed(futures):
            try:
                print(*future.result(), flush=True)
            except Exception as exc:
                print("FAILED", futures[future], str(exc), flush=True)


def fence(text, language="text"):
    marker = "`" * max(3, max((len(run) + 1 for run in re.findall(r"`+", text)), default=0))
    return f"{marker}{language}\n{text}{'' if text.endswith(chr(10)) else chr(10)}{marker}\n"


def poc_evidence(page, readable):
    """Return explicit PoC evidence, or None when a page has no usable PoC."""
    attachments = SOURCE_ATTACHMENT.findall(page)
    if attachments:
        return {"kind": "source_attachment", "evidence": attachments[0]}
    for block in CODE_BLOCK.findall(page):
        code = html.unescape(re.sub(r"<[^>]+>", "", block)).strip()
        if CODE_SIGNAL.search(code) and (POC_MARKER.search(readable) or "ruby" in code.lower()):
            return {"kind": "embedded_code", "evidence": code[:500]}
    return None


def render_reports(numbers):
    REPORTS.mkdir(parents=True, exist_ok=True)
    manifest, excluded = [], []
    for number in numbers:
        raw_path = RAW / f"ruby_{number}.html"
        if not raw_path.exists():
            print("MISSING", number)
            continue
        raw = raw_path.read_bytes()
        page, readable = raw.decode("utf-8", errors="replace"), text_from_html(raw)
        poc = poc_evidence(page, readable)
        if not poc:
            excluded.append({"number": number, "reason": "no explicit runnable PoC or source attachment found"})
            continue
        match = TITLE.search(page)
        title = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip() if match else f"Ruby issue #{number}"
        title = title.replace("\n", " ").strip()
        issue_url = f"{BASE_URL}/issues/{number}"
        out = f"# CRuby #{number}: {title}\n\n## Metadata\n\n- Issue: [{title}]({issue_url})\n"
        out += f"- Retrieved: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n- Source SHA-256: `{hashlib.sha256(raw).hexdigest()}`\n\n"
        out += "## Readable Source Record\n\n" + fence(readable) + "\n"
        out += "## Raw Redmine Source\n\nThe complete fetched issue page is preserved below and in the cached HTML file.\n\n" + fence(page, "html") + "\n"
        if not DIAGNOSTIC.search(readable):
            out += "## Sanitizer Output Availability\n\nNo sanitizer diagnostic marker found in this issue page.\n"
        (REPORTS / f"ruby_{number}.md").write_text(out)
        manifest.append({"number": number, "title": title, "diagnostic_source_record": bool(DIAGNOSTIC.search(readable)), "poc": poc, "source_sha256": hashlib.sha256(raw).hexdigest()})
    (REPORTS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (REPORTS / "excluded_no_poc.json").write_text(json.dumps(excluded, indent=2) + "\n")
    index = "# CRuby bug instance reports\n\n| Issue | Title | Sanitizer record |\n|---|---|---|\n"
    for record in manifest:
        index += f'| [#{record["number"]}](ruby_{record["number"]}.md) | {record["title"].replace("|", "\\|")} | {"Yes" if record["diagnostic_source_record"] else "—"} |\n'
    (REPORTS / "index.md").write_text(index)
    print(f"{len(manifest)} reports rendered; {len(excluded)} excluded for no explicit PoC")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discover", action="store_true", help="scrape and cache all project Bug issue IDs")
    parser.add_argument("--all-candidates", action="store_true", help="use the full discovered Bug list instead of sanitizer candidates")
    parser.add_argument("--sources", action="store_true", help="fetch and cache issue pages")
    parser.add_argument("--render", action="store_true", help="render cached issue pages as Markdown")
    parser.add_argument("--max-pages", type=int, help="limit project-list pages during discovery")
    args = parser.parse_args()
    selected = [args.discover, args.sources, args.render]
    if args.discover:
        numbers = discover(args.max_pages)
    elif args.all_candidates:
        numbers = issue_numbers(args.max_pages)
    else:
        numbers = candidate_numbers()
    if not any(selected) or args.sources:
        collect_sources(numbers)
    if not any(selected) or args.render:
        render_reports(numbers)


if __name__ == "__main__":
    main()

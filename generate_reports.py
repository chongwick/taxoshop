#!/usr/bin/env python3
"""Collect CPython bug evidence and render structured, verbatim reports.

Run without arguments to execute every stage.  The individual flags are useful
when resuming a partially completed collection; existing API/download caches
are retained in every case.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "taxos" / "micro_taxo"
SOURCES = REPORTS / "sources"
ATTACHMENTS = SOURCES / "attachments"
FIXES = SOURCES / "fixes"
BUGS = ROOT / "taxos" / "bugs.txt"
NUMBERS = re.findall(r"/issues/(\d+)", BUGS.read_text())
DIAGNOSTIC = re.compile(
    r"(?:Address|Leak|Memory|Thread|UndefinedBehavior)Sanitizer"
    r"|runtime error:|==\d+==|Invalid (?:read|write|free)|HEAP SUMMARY|ERROR SUMMARY",
    re.I,
)
LINKED_PRS = re.compile(r"<!-- gh-linked-prs -->(.*?)<!-- /gh-linked-prs -->", re.S)
GH_PR_REF = re.compile(r"\bgh-(\d+)\b")
PR_URL = re.compile(r"https://github\.com/python/cpython/pull/(\d+)")
COMMIT_URL = re.compile(r"https://github\.com/python/cpython/commit/([0-9a-f]{7,40})")
HG_CHANGESET = re.compile(r"^New changeset ([0-9a-f]+) by .+ in branch .+", re.M)
FIXED_BY = re.compile(r"Fixed by[:\s]+(https?://\S+)", re.I)
ATTACHMENT_URL = re.compile(
    r"https://github\.com/(?:[^\s<>]+?/files/|user-attachments/files/)[^\s<>\)\]\"`]+"
)


def api(endpoint):
    """Call GitHub's CLI API, retrying transient failures."""
    for attempt in range(4):
        result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        time.sleep(2**attempt)
    raise RuntimeError(result.stderr.strip())


def api_paginated(endpoint):
    results = []
    page = 1
    while True:
        separator = "&" if "?" in endpoint else "?"
        batch = api(f"{endpoint}{separator}per_page=100&page={page}")
        results.extend(batch)
        if len(batch) < 100:
            return results
        page += 1


def collect_source(number):
    path = SOURCES / f"gh_{number}.json"
    if path.exists():
        return number, "cached"
    issue = api(f"repos/python/cpython/issues/{number}")
    comments = api_paginated(f"repos/python/cpython/issues/{number}/comments") if issue["comments"] else []
    data = {
        "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "issue": issue,
        "comments": comments,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return number, f"{len(comments)} comments"


def collect_sources():
    SOURCES.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(collect_source, n): n for n in dict.fromkeys(NUMBERS)}
        for future in concurrent.futures.as_completed(futures):
            try:
                print(*future.result(), flush=True)
            except Exception as exc:
                print("FAILED", futures[future], str(exc), flush=True)


def attachment_urls():
    urls = {}
    for path in SOURCES.glob("gh_*.json"):
        data = json.loads(path.read_text())
        for obj in [data["issue"], *data["comments"]]:
            for url in ATTACHMENT_URL.findall(obj.get("body") or ""):
                url = url.rstrip(";,.:")
                if re.search(r"\.(txt|log|out|patch|py|c)$", url, re.I):
                    urls.setdefault(url, []).append(obj["html_url"])
    return urls


def download_attachment(item):
    url, references = item
    name = hashlib.sha256(url.encode()).hexdigest()[:12] + "_" + url.rsplit("/", 1)[-1]
    path = ATTACHMENTS / name
    result = subprocess.run(
        ["curl", "--fail", "--silent", "--show-error", "--location", "--max-time", "90", url,
         "--output", str(path)],
        capture_output=True,
        text=True,
    )
    output = {"url": url, "references": references, "path": name, "success": result.returncode == 0}
    if result.returncode:
        output["error"] = result.stderr
    else:
        output["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(name, output["success"], flush=True)
    return output


def collect_attachments():
    ATTACHMENTS.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(download_attachment, attachment_urls().items()))
    (ATTACHMENTS / "manifest.json").write_text(json.dumps(results, indent=2) + "\n")


def collect_pr(number):
    path = FIXES / f"pr_{number}.json"
    if path.exists():
        return number, "cached"
    data = {
        "pr": api(f"repos/python/cpython/pulls/{number}"),
        "files": api_paginated(f"repos/python/cpython/pulls/{number}/files"),
        "review_comments": api_paginated(f"repos/python/cpython/pulls/{number}/comments"),
        "issue_comments": api_paginated(f"repos/python/cpython/issues/{number}/comments"),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return number, f'{len(data["files"])} files, {len(data["review_comments"])} review comments'


def collect_commit(sha):
    path = FIXES / f"commit_{sha}.json"
    if path.exists():
        return sha, "cached"
    commit = api(f"repos/python/cpython/commits/{sha}")
    path.write_text(json.dumps(commit, ensure_ascii=False, indent=2) + "\n")
    return sha, f'{len(commit.get("files", []))} files'


def gather_fix_refs():
    prs, commits = set(), set()
    for number in NUMBERS:
        path = SOURCES / f"gh_{number}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        objects = [data["issue"], *data["comments"]]
        linked = LINKED_PRS.search(data["issue"].get("body") or "")
        if linked:
            prs.update(GH_PR_REF.findall(linked.group(1)))
        for obj in objects:
            text = obj.get("body") or ""
            prs.update(PR_URL.findall(text))
            commits.update(COMMIT_URL.findall(text))
    return sorted(prs, key=int), sorted(commits)


def collect_fixes():
    FIXES.mkdir(parents=True, exist_ok=True)
    prs, commits = gather_fix_refs()
    print(f"Collecting {len(prs)} PRs and {len(commits)} standalone commits...")
    for prefix, values, collector in (("PR", prs, collect_pr), ("COMMIT", commits, collect_commit)):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(collector, value): value for value in values}
            for future in concurrent.futures.as_completed(futures):
                try:
                    print(prefix, *future.result(), flush=True)
                except Exception as exc:
                    print(f"FAILED {prefix}", futures[future], str(exc), flush=True)


def fence(text, language="text"):
    length = max([3] + [len(run) + 1 for run in re.findall(r"`+", text)])
    marker = "`" * length
    return marker + language + "\n" + text + ("" if text.endswith("\n") else "\n") + marker + "\n"


def extract_fix_refs(objects):
    linked = LINKED_PRS.search(objects[0].get("body") or "")
    linked_prs = GH_PR_REF.findall(linked.group(1)) if linked else []
    return (
        linked_prs,
        list(dict.fromkeys(pr for obj in objects for pr in PR_URL.findall(obj.get("body") or ""))),
        list(dict.fromkeys(sha for obj in objects for sha in COMMIT_URL.findall(obj.get("body") or ""))),
        list(dict.fromkeys(cs for obj in objects for cs in HG_CHANGESET.findall(obj.get("body") or ""))),
        list(dict.fromkeys(url.rstrip(".,;)") for obj in objects for url in FIXED_BY.findall(obj.get("body") or ""))),
    )


def render_pr(number):
    path = FIXES / f"pr_{number}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    pr = data["pr"]
    out = f'### PR #{number}: {pr["title"]}\n\n'
    out += f'- URL: [{pr["html_url"]}]({pr["html_url"]})\n- State: {pr["state"]}'
    if pr.get("merged_at"):
        out += f'; merged: {pr["merged_at"]}'
        if pr.get("merge_commit_sha"):
            sha = pr["merge_commit_sha"]
            out += f'; merge commit: [`{sha[:12]}`](https://github.com/python/cpython/commit/{sha})'
    elif pr.get("closed_at"):
        out += f'; closed (not merged): {pr["closed_at"]}'
    out += f'\n- Author: {pr["user"]["login"]}\n- Changes: +{pr["additions"]} / -{pr["deletions"]} across {pr["changed_files"]} file(s)\n'
    if pr.get("body"):
        out += "\n#### Description\n\n" + fence(pr["body"]) + "\n"
    if data["files"]:
        out += "#### Changed Files\n\n"
        for file in data["files"]:
            out += f'##### `{file["filename"]}` ({file.get("status", "")}; +{file["additions"]} / -{file["deletions"]})\n\n'
            out += fence(file["patch"], "diff") + "\n" if file.get("patch") else "No patch available (binary or too large).\n\n"
    by_file = {}
    for comment in data["review_comments"]:
        by_file.setdefault(comment["path"], []).append(comment)
    if by_file:
        out += "#### Review Comments\n\n"
        for filename, comments in sorted(by_file.items()):
            out += f"##### `{filename}`\n\n"
            for comment in comments:
                out += f'**{comment["user"]["login"]}**, {comment["created_at"]}:\n\n'
                if comment.get("diff_hunk"):
                    out += fence(comment["diff_hunk"], "diff") + "\n"
                out += fence(comment["body"]) + "\n"
    if data["issue_comments"]:
        out += "#### PR Discussion\n\n"
        for comment in data["issue_comments"]:
            out += f'**{comment["user"]["login"]}**, {comment["created_at"]}:\n\n' + fence(comment["body"]) + "\n"
    return out


def render_commit(sha):
    path = FIXES / f"commit_{sha}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    commit = data.get("commit", {})
    out = f"### Commit [`{sha[:12]}`](https://github.com/python/cpython/commit/{sha})\n\n"
    out += f'- Author: {commit.get("author", {}).get("name", "unknown")}, {commit.get("author", {}).get("date", "")}\n'
    if (message := (commit.get("message") or "").strip()):
        out += "\n#### Commit Message\n\n" + fence(message) + "\n"
    if data.get("files"):
        out += "#### Changed Files\n\n"
        for file in data["files"]:
            out += f'##### `{file["filename"]}` ({file.get("status", "")}; +{file["additions"]} / -{file["deletions"]})\n\n'
            out += fence(file["patch"], "diff") + "\n" if file.get("patch") else "No patch available (binary or too large).\n\n"
    return out


def render_reports():
    attachment_manifest = ATTACHMENTS / "manifest.json"
    attachments = json.loads(attachment_manifest.read_text()) if attachment_manifest.exists() else []
    manifest = []
    for number in NUMBERS:
        path = SOURCES / f"gh_{number}.json"
        if not path.exists():
            print("MISSING", number)
            continue
        data = json.loads(path.read_text())
        issue, objects = data["issue"], [data["issue"], *data["comments"]]
        labels = ", ".join(label["name"] for label in issue.get("labels", []))
        out = f'# CPython #{number}: {issue["title"]}\n\n## Metadata\n\n'
        out += f'- Issue: [{issue["title"]}]({issue["html_url"]})\n- Created: {issue["created_at"]}\n- Updated: {issue["updated_at"]}\n- Retrieved: {data["retrieved_at"]}\n'
        out += f'- Status: {issue["state"]}; closed: {issue.get("closed_at") or "not closed"}\n- Labels: {labels or "none"}\n- Comments: {len(data["comments"])}\n\n'
        linked_prs, fix_prs, fix_commits, changesets, fixed_by_urls = extract_fix_refs(objects)
        has_fix = any([linked_prs, fix_prs, fix_commits, changesets, fixed_by_urls])
        all_prs = list(dict.fromkeys(linked_prs + fix_prs))
        merge_shas = {json.loads((FIXES / f"pr_{pr}.json").read_text())["pr"].get("merge_commit_sha") for pr in all_prs if (FIXES / f"pr_{pr}.json").exists()}
        sections = [section for pr in all_prs if (section := render_pr(pr))]
        sections += [section for sha in fix_commits if sha not in merge_shas if (section := render_commit(sha))]
        out += "## Fix Data\n\n"
        if sections:
            out += "\n".join(sections)
        elif changesets:
            out += "Mercurial changesets (pre-GitHub era; patch data not fetched): " + ", ".join(f"`{cs}`" for cs in changesets) + "\n\n"
        elif has_fix:
            out += "Fix references exist but fix data has not been collected yet. Run this script with `--fixes`.\n\n"
        else:
            out += "No fix references found in the issue or comments.\n\n"
        out += "## Source Records\n\nComplete verbatim content of the issue body and every comment. Sanitizer stacks, shadow bytes, allocation/free histories, and reproducers are preserved exactly as posted.\n\n"
        diagnostic_count = 0
        for index, obj in enumerate(objects):
            text = obj.get("body") or ""
            heading = "Original Issue" if index == 0 else f'Comment {index} — {obj["user"]["login"]}, {obj["created_at"]}'
            url = obj["html_url"]
            out += f"### {heading}\n\nSource: [{url}]({url})\n\n" + fence(text) + "\n"
            diagnostic_count += bool(DIAGNOSTIC.search(text))
        related = [attachment for attachment in attachments if any(obj["html_url"] in attachment["references"] for obj in objects)]
        if related:
            out += "## Linked Text Attachments\n\n"
            for attachment in related:
                out += f'### [{attachment["path"]}]({attachment["url"]})\n\n'
                if attachment["success"]:
                    raw = (ATTACHMENTS / attachment["path"]).read_bytes()
                    try:
                        out += fence(raw.decode("utf-8")) + "\n"
                    except UnicodeDecodeError:
                        out += "Binary attachment; not UTF-8 text.\n\n"
                    out += f'Local copy: [original attachment](sources/attachments/{attachment["path"]}); SHA-256: `{attachment["sha256"]}`.\n\n'
                else:
                    out += "Retrieval failed: " + attachment.get("error", "unknown error").strip() + "\n\n"
        if not diagnostic_count:
            out += "## Sanitizer Output Availability\n\nNo sanitizer diagnostic marker found in the issue body or comments.\n"
        (REPORTS / f"gh_{number}.md").write_bytes(out.encode("utf-8"))
        assert all((obj.get("body") or "").encode("utf-8") in out.encode("utf-8") for obj in objects), f"Source body not found verbatim in output for #{number}"
        manifest.append({"number": int(number), "title": issue["title"], "comments": len(data["comments"]), "diagnostic_source_records": diagnostic_count, "has_fix_references": has_fix, "fix_data_collected": bool(sections), "attachments": len(related), "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (REPORTS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    index = "# CPython bug instance reports\n\n" + f"{len(manifest)} reports. Each file contains the full issue body and all comments verbatim.\n\n| Issue | Title | Sanitizer records | Fix data |\n|---|---|---|---|\n"
    for record in manifest:
        title = record["title"].replace("|", "\\|").replace("\n", " ")
        fix = "Yes" if record["fix_data_collected"] else ("Refs only" if record["has_fix_references"] else "—")
        index += f'| [#{record["number"]}](gh_{record["number"]}.md) | {title} | {record["diagnostic_source_records"]} | {fix} |\n'
    (REPORTS / "index.md").write_text(index)
    print(f'{len(manifest)} reports; {sum(record["diagnostic_source_records"] for record in manifest)} records with sanitizer output; {sum(record["fix_data_collected"] for record in manifest)} with fix data; all source-body byte checks passed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    stages = parser.add_argument_group("stages")
    stages.add_argument("--sources", action="store_true", help="collect issue bodies and comments")
    stages.add_argument("--attachments", action="store_true", help="download linked text attachments")
    stages.add_argument("--fixes", action="store_true", help="collect linked PR and commit data")
    stages.add_argument("--render", action="store_true", help="render Markdown reports")
    args = parser.parse_args()
    selected = [args.sources, args.attachments, args.fixes, args.render]
    if not any(selected) or args.sources:
        collect_sources()
    if not any(selected) or args.attachments:
        collect_attachments()
    if not any(selected) or args.fixes:
        collect_fixes()
    if not any(selected) or args.render:
        render_reports()


if __name__ == "__main__":
    main()

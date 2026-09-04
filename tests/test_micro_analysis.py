import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPOSITORY_ROOT / "micro-analysis.py"
SPEC = importlib.util.spec_from_file_location("micro_analysis", MODULE_PATH)
micro_analysis = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = micro_analysis
SPEC.loader.exec_module(micro_analysis)


class FakeGitHubClient:
    def __init__(self, issues):
        self.issues = issues

    def fetch_issue(self, reference):
        return self.issues[reference.number]


class FakeDrafter:
    def __init__(self):
        self.prompts = []

    def draft(self, issue, template):
        self.prompts.append((issue, template))
        return template.replace(
            "GH-XXXXX — <Short Bug Title>",
            f"GH-{issue.number} — {issue.title}",
        ).replace("issues/XXXXX", f"issues/{issue.number}")


class MicroAnalysisTests(unittest.TestCase):
    def test_render_source_record_preserves_issue_comment_fix_and_raw_payload_evidence(self):
        issue_url = "https://github.com/python/cpython/issues/100086"
        pull_request_url = "https://github.com/python/cpython/pull/123456"
        commit_url = "https://github.com/python/cpython/commit/abcdef123456"
        issue_payload = {
            "number": 100086,
            "html_url": issue_url,
            "title": "Preserve source evidence",
            "state": "closed",
            "body": f"Fixed by {pull_request_url}.",
            "unknown_github_field": "preserve me exactly",
        }
        comment_payloads = (
            {
                "html_url": f"{issue_url}#issuecomment-1",
                "body": f"Landed in {commit_url}.",
                "user": {"login": "maintainer"},
                "created_at": "2026-09-04T12:00:00Z",
                "unknown_comment_field": "also preserve me",
            },
        )
        issue = micro_analysis.GitHubIssue(
            number=100086,
            url=issue_url,
            title="Preserve source evidence",
            state="closed",
            body=issue_payload["body"],
            labels=("bug",),
            comments=(
                micro_analysis.IssueComment(
                    author="maintainer",
                    body=comment_payloads[0]["body"],
                    url=comment_payloads[0]["html_url"],
                    created_at=comment_payloads[0]["created_at"],
                ),
            ),
            issue_payload=issue_payload,
            comment_payloads=comment_payloads,
        )

        rendered = micro_analysis.render_source_record(
            issue,
            (REPOSITORY_ROOT / "templates/micro-taxo-template.md").read_text(
                encoding="utf-8"
            ),
            retrieved_at="2026-09-04T12:34:56Z",
        )

        self.assertIn(issue_payload["body"], rendered)
        self.assertIn(comment_payloads[0]["body"], rendered)
        self.assertIn(pull_request_url, rendered)
        self.assertIn(commit_url, rendered)
        self.assertIn(json.dumps(issue_payload, indent=2, sort_keys=True), rendered)
        self.assertIn("unknown_github_field", rendered)

    def test_parse_issue_urls_ignores_comments_and_deduplicates(self):
        input_text = """\
# CPython bugs
https://github.com/python/cpython/issues/100086

https://github.com/python/cpython/issues/100086
https://github.com/python/cpython/issues/101180#comment
"""

        references = micro_analysis.parse_issue_urls(input_text)

        self.assertEqual([reference.number for reference in references], [100086, 101180])

    def test_run_writes_a_draft_for_each_issue_and_only_open_issues_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "issues.txt"
            template_path = root / "template.md"
            output_dir = root / "micro_taxos"
            open_issues_path = root / "open_github_issues.txt"
            input_path.write_text(
                "https://github.com/python/cpython/issues/100086\n"
                "https://github.com/python/cpython/issues/101180\n",
                encoding="utf-8",
            )
            template = (REPOSITORY_ROOT / "templates/micro-taxo-template.md").read_text(
                encoding="utf-8"
            )
            template_path.write_text(template, encoding="utf-8")
            issues = {
                100086: micro_analysis.GitHubIssue(
                    number=100086,
                    url="https://github.com/python/cpython/issues/100086",
                    title="Open bug",
                    state="open",
                    body="An open bug report.",
                    labels=("bug",),
                    comments=(),
                ),
                101180: micro_analysis.GitHubIssue(
                    number=101180,
                    url="https://github.com/python/cpython/issues/101180",
                    title="Closed bug",
                    state="closed",
                    body="A closed bug report.",
                    labels=(),
                    comments=(),
                ),
            }
            drafter = FakeDrafter()

            summary = micro_analysis.run_analysis(
                input_path=input_path,
                template_path=template_path,
                output_dir=output_dir,
                open_issues_path=open_issues_path,
                github_client=FakeGitHubClient(issues),
                drafter=drafter,
            )

            self.assertEqual(summary.processed, 2)
            self.assertEqual(summary.open_issues, 1)
            self.assertEqual(summary.failures, ())
            self.assertEqual(len(drafter.prompts), 2)
            self.assertTrue((output_dir / "gh_100086.md").is_file())
            self.assertTrue((output_dir / "gh_101180.md").is_file())
            self.assertIn("GH-100086 — Open bug", (output_dir / "gh_100086.md").read_text())
            report = open_issues_path.read_text(encoding="utf-8")
            self.assertIn("#100086: Open bug", report)
            self.assertNotIn("#101180", report)


if __name__ == "__main__":
    unittest.main()

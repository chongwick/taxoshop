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


class RecordingFingerprintGenerator:
    def __init__(self, micro_taxo_path):
        self.micro_taxo_path = micro_taxo_path
        self.micro_taxo_existed_on_generate = False

    def generate(self, micro_taxo, template):
        self.micro_taxo_existed_on_generate = self.micro_taxo_path.is_file()
        return template


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
        self.assertIn(json.dumps(comment_payloads, indent=2, sort_keys=True), rendered)
        self.assertIn("unknown_comment_field", rendered)

    def test_parse_issue_urls_ignores_comments_and_deduplicates(self):
        input_text = """\
# CPython bugs
https://github.com/python/cpython/issues/100086

https://github.com/python/cpython/issues/100086
https://github.com/python/cpython/issues/101180#comment
"""

        references = micro_analysis.parse_issue_urls(input_text)

        self.assertEqual([reference.number for reference in references], [100086, 101180])

    def test_run_writes_fingerprint_after_matching_micro_taxo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "issues.txt"
            template_path = root / "template.md"
            output_dir = root / "micro_taxos"
            open_issues_path = root / "open_github_issues.txt"
            fingerprint_template_path = REPOSITORY_ROOT / "templates/fingerprint-template.md"
            fingerprint_dir = root / "fingerprints"
            input_path.write_text(
                "https://github.com/python/cpython/issues/100086\n",
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
                    title="Source record then fingerprint",
                    state="closed",
                    body="Issue evidence.",
                    labels=("bug",),
                    comments=(),
                ),
            }
            micro_taxo_path = output_dir / "gh_100086.md"
            generator = RecordingFingerprintGenerator(micro_taxo_path)

            summary = micro_analysis.run_analysis(
                input_path=input_path,
                template_path=template_path,
                output_dir=output_dir,
                open_issues_path=open_issues_path,
                fingerprint_template_path=fingerprint_template_path,
                fingerprint_dir=fingerprint_dir,
                github_client=FakeGitHubClient(issues),
                fingerprint_generator=generator,
            )

            self.assertTrue(generator.micro_taxo_existed_on_generate)
            self.assertTrue((fingerprint_dir / "gh_100086.md").is_file())
            self.assertEqual(summary.processed, 1)
            self.assertEqual(summary.open_issues, 0)
            self.assertEqual(summary.failures, ())


if __name__ == "__main__":
    unittest.main()

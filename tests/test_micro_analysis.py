import importlib.util
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


class StubGitHubClient(micro_analysis.GitHubClient):
    def __init__(self, pages):
        super().__init__()
        self.pages = pages
        self.requested_urls = []

    def _get_json_with_headers(self, url):
        self.requested_urls.append(url)
        return self.pages[url]


class RecordingFingerprintGenerator:
    def __init__(self, micro_taxo_path):
        self.micro_taxo_path = micro_taxo_path
        self.micro_taxo_existed_on_generate = False

    def generate(self, micro_taxo, template):
        self.micro_taxo_existed_on_generate = self.micro_taxo_path.is_file()
        return template


class FailingFingerprintGenerator:
    def generate(self, micro_taxo, template):
        raise RuntimeError("Codex fingerprint generation failed")


class MicroAnalysisTests(unittest.TestCase):
    def test_extract_evidence_blocks_keeps_code_and_sanitizer_output_verbatim(self):
        source_label = "issue body"
        source_url = "https://example.test/issues/42"
        sanitizer_output = (
            "==1==ERROR: AddressSanitizer: heap-use-after-free on address 0x0\n"
            "READ of size 8 at 0x0 thread T0\n"
            "    #0 0xdeadbeef in trigger poc.py:3"
        )
        text = f"""```python
trigger()
```
```text
{sanitizer_output}
```"""

        evidence = micro_analysis.extract_evidence_blocks(
            text, source_label, source_url
        )

        code_block = evidence.code_blocks[0]
        sanitizer_block = evidence.sanitizer_blocks[0]
        self.assertEqual(code_block.content, "trigger()")
        self.assertEqual(code_block.source_label, source_label)
        self.assertEqual(code_block.source_url, source_url)
        self.assertEqual(sanitizer_block.content, sanitizer_output)
        self.assertEqual(sanitizer_block.source_label, source_label)
        self.assertEqual(sanitizer_block.source_url, source_url)

    def test_fetch_issue_collects_all_comment_pages(self):
        issue_url = "https://github.com/python/cpython/issues/42"
        issue_endpoint = "https://api.github.com/repos/python/cpython/issues/42"
        comments_endpoint = "https://api.example/comments?per_page=100"
        next_comments_endpoint = "https://api.example/comments?page=2"
        issue_payload = {
            "number": 42,
            "html_url": issue_url,
            "title": "Paginate comments",
            "state": "closed",
            "body": "Issue body",
            "labels": [],
            "comments": 2,
            "comments_url": "https://api.example/comments",
        }
        first_comment = {
            "id": 1,
            "body": "first",
            "user": {"login": "first-author"},
            "html_url": f"{issue_url}#issuecomment-1",
            "created_at": "2026-01-01T00:00:00Z",
        }
        last_comment = {
            "id": 2,
            "body": "last",
            "user": {"login": "last-author"},
            "html_url": f"{issue_url}#issuecomment-2",
            "created_at": "2026-01-02T00:00:00Z",
            "unknown_comment_field": "retain me",
        }
        client = StubGitHubClient(
            {
                issue_endpoint: (issue_payload, ""),
                comments_endpoint: (
                    [first_comment],
                    f'<{next_comments_endpoint}>; rel="next", '
                    '<https://api.example/comments?page=2>; rel="last"',
                ),
                next_comments_endpoint: ([last_comment], ""),
            }
        )

        issue = client.fetch_issue(
            micro_analysis.IssueReference("python", "cpython", 42, issue_url)
        )

        self.assertEqual([comment.body for comment in issue.comments], ["first", "last"])
        self.assertEqual(issue.comment_payloads, (first_comment, last_comment))
        self.assertEqual(
            client.requested_urls,
            [issue_endpoint, comments_endpoint, next_comments_endpoint],
        )

    def test_parse_issue_urls_ignores_comments_and_deduplicates(self):
        input_text = """\
# CPython bugs
https://github.com/python/cpython/issues/100086

https://github.com/python/cpython/issues/100086
https://github.com/python/cpython/issues/101180#comment
"""

        references = micro_analysis.parse_issue_urls(input_text)

        self.assertEqual([reference.number for reference in references], [100086, 101180])

    def test_run_writes_the_compact_report_template_before_fingerprinting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "issues.txt"
            template_path = root / "template.md"
            output_dir = root / "micro_taxos"
            open_issues_path = root / "open_github_issues.txt"
            fingerprint_dir = root / "fingerprints"
            input_path.write_text(
                "https://github.com/python/cpython/issues/100086\n", encoding="utf-8"
            )
            template_path.write_text(
                (REPOSITORY_ROOT / "templates/micro-taxo-template.md").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            issue = micro_analysis.GitHubIssue(
                number=100086,
                url="https://github.com/python/cpython/issues/100086",
                title="Record only",
                state="open",
                body="Exact source body.",
                labels=("bug",),
                comments=(),
                issue_payload={"unknown_github_field": "retained"},
            )

            summary = micro_analysis.run_analysis(
                input_path=input_path,
                template_path=template_path,
                output_dir=output_dir,
                open_issues_path=open_issues_path,
                fingerprint_template_path=REPOSITORY_ROOT
                / "templates/fingerprint-template.md",
                fingerprint_dir=fingerprint_dir,
                github_client=FakeGitHubClient({100086: issue}),
                fingerprint_generator=RecordingFingerprintGenerator(
                    output_dir / "gh_100086.md"
                ),
            )

            report = (output_dir / "gh_100086.md").read_text(encoding="utf-8")
            self.assertIn("## Bug Report", report)
            self.assertIn("## Full Sanitizer / Crash Output", report)
            self.assertIn("#100086", open_issues_path.read_text(encoding="utf-8"))
            self.assertEqual(summary.processed, 1)
            self.assertEqual(summary.open_issues, 1)
            self.assertEqual(summary.failures, ())

    def test_run_keeps_compact_report_when_fingerprint_generation_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "issues.txt"
            template_path = root / "template.md"
            output_dir = root / "micro_taxos"
            fingerprint_dir = root / "fingerprints"
            open_issues_path = root / "open_github_issues.txt"
            input_path.write_text(
                "https://github.com/python/cpython/issues/100086\n", encoding="utf-8"
            )
            template_path.write_text(
                (REPOSITORY_ROOT / "templates/micro-taxo-template.md").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            issue = micro_analysis.GitHubIssue(
                number=100086,
                url="https://github.com/python/cpython/issues/100086",
                title="Fingerprint failure",
                state="open",
                body="Source evidence is retained.",
                labels=(),
                comments=(),
            )

            summary = micro_analysis.run_analysis(
                input_path=input_path,
                template_path=template_path,
                output_dir=output_dir,
                open_issues_path=open_issues_path,
                fingerprint_template_path=REPOSITORY_ROOT
                / "templates/fingerprint-template.md",
                fingerprint_dir=fingerprint_dir,
                github_client=FakeGitHubClient({100086: issue}),
                fingerprint_generator=FailingFingerprintGenerator(),
            )

            self.assertTrue((output_dir / "gh_100086.md").is_file())
            self.assertFalse((fingerprint_dir / "gh_100086.md").exists())
            self.assertIn("#100086", open_issues_path.read_text(encoding="utf-8"))
            self.assertEqual(summary.processed, 0)
            self.assertEqual(summary.open_issues, 1)
            self.assertEqual(len(summary.failures), 1)
            self.assertIn("Codex fingerprint generation failed", summary.failures[0])

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

    def test_parser_uses_fingerprint_defaults(self):
        args = micro_analysis.build_parser().parse_args([])

        self.assertEqual(
            args.fingerprint_template,
            Path("templates/fingerprint-template.md"),
        )
        self.assertEqual(args.fingerprint_dir, Path("workdir_python/fingerprints"))


if __name__ == "__main__":
    unittest.main()

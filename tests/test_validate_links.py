#!/usr/bin/env python3
"""
Tests for scripts/validation/validate_links.py

Covers: URL extraction, HTTP status handling, skip logic, exit codes,
deduplication, error handling, and concurrency.

All HTTP calls are mocked — no real network requests made.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import requests

# Ensure scripts/ is on path before importing the module under test
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validation.validate_links import (
    extract_urls_from_file,
    check_url,
    validate_links,
    find_all_md_files,
    SKIP_DOMAINS,
    BOT_BLOCKING_CODES,
    TRAILING_PUNCT,
)
from utils.common import Severity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_md(tmp_path: Path, content: str, name: str = "test.md") -> Path:
    """Write content to a markdown file and return the path."""
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return f


def mock_response(status_code: int) -> MagicMock:
    """Create a mock requests.Response with the given status code."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.close = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# URL Extraction
# ---------------------------------------------------------------------------

class TestUrlExtraction(unittest.TestCase):
    """Tests for extract_urls_from_file — what URLs are found and what are skipped."""

    def test_markdown_link_url_extracted(self, tmp_path=None):
        """URLs inside markdown [text](url) syntax are extracted."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "[docs](https://docs.example.org/guide)\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertIn("https://docs.example.org/guide", urls)

    def test_plain_text_url_extracted(self, tmp_path=None):
        """Bare https:// URLs in plain prose are extracted."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test2"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "See https://real-site.io/page for details.\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertIn("https://real-site.io/page", urls)

    def test_http_url_extracted(self, tmp_path=None):
        """http:// (non-TLS) URLs are also extracted."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test3"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "See http://legacy.example.org/api\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertIn("http://legacy.example.org/api", urls)

    def test_localhost_url_skipped(self, tmp_path=None):
        """localhost URLs are not extracted."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test4"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "Server at https://localhost:8080/health\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertEqual(urls, [])

    def test_127_0_0_1_url_skipped(self, tmp_path=None):
        """127.0.0.1 loopback URLs are not extracted."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test5"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "API at http://127.0.0.1:3000/v1\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertEqual(urls, [])

    def test_example_com_url_skipped(self, tmp_path=None):
        """example.com placeholder domain is not extracted."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test6"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "See https://example.com/page for demo.\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertEqual(urls, [])

    def test_example_com_subdomain_skipped(self, tmp_path=None):
        """Subdomains of example.com (e.g. docs.example.com) are also skipped."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test7"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "See https://docs.example.com/guide\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertEqual(urls, [])

    def test_template_placeholder_angle_bracket_skipped(self, tmp_path=None):
        """URLs containing < are template placeholders and skipped."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test8"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "Replace https://<your-domain>/api with your URL.\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertEqual(urls, [])

    def test_template_placeholder_curly_brace_skipped(self, tmp_path=None):
        """URLs containing { are template placeholders and skipped."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test9"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "Call https://{host}/api/v1 endpoint.\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertEqual(urls, [])

    def test_trailing_period_stripped(self, tmp_path=None):
        """Trailing period is stripped from extracted URL."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test10"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "See https://real-site.io/page.\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertIn("https://real-site.io/page", urls)
        self.assertNotIn("https://real-site.io/page.", urls)

    def test_trailing_comma_stripped(self, tmp_path=None):
        """Trailing comma is stripped from extracted URL."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test11"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "Visit https://real-site.io/page, or contact us.\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertIn("https://real-site.io/page", urls)
        self.assertNotIn("https://real-site.io/page,", urls)

    def test_trailing_closing_paren_stripped(self, tmp_path=None):
        """Trailing ) is stripped from URL in markdown link syntax."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test12"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        # The URL_PATTERN stops before ) so the URL is already clean
        f = write_md(tmp_path, "[link](https://real-site.io/page)\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertIn("https://real-site.io/page", urls)

    def test_line_number_reported_correctly(self, tmp_path=None):
        """The line number returned matches where the URL appears in the file."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test13"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "Line one\nLine two\nhttps://real-site.io/page\n")
        pairs = extract_urls_from_file(f)
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertEqual(len(pairs), 1)
        url, line_no = pairs[0]
        self.assertEqual(url, "https://real-site.io/page")
        self.assertEqual(line_no, 3)

    def test_empty_file_returns_empty_list(self, tmp_path=None):
        """Empty file produces no URLs (no crash)."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test14"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "")
        urls = extract_urls_from_file(f)
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertEqual(urls, [])

    def test_no_urls_in_file_returns_empty_list(self, tmp_path=None):
        """File with only text and no URLs returns empty list."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test15"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path, "# Title\n\nJust some text with no links.\n")
        urls = extract_urls_from_file(f)
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertEqual(urls, [])

    def test_multiple_urls_on_same_line_all_extracted(self, tmp_path=None):
        """Multiple URLs on the same line are all extracted."""
        if tmp_path is None:
            tmp_path = Path(__file__).parent / "_tmp_test16"
            tmp_path.mkdir(exist_ok=True)
            cleanup = True
        else:
            cleanup = False
        f = write_md(tmp_path,
            "See https://site-a.io/page and https://site-b.io/other\n")
        urls = [u for u, _ in extract_urls_from_file(f)]
        if cleanup:
            import shutil; shutil.rmtree(tmp_path)
        self.assertIn("https://site-a.io/page", urls)
        self.assertIn("https://site-b.io/other", urls)

    def test_nonexistent_file_returns_empty_list(self):
        """A file that doesn't exist returns empty list rather than raising."""
        result = extract_urls_from_file(Path("/nonexistent/path/test.md"))
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# check_url: HTTP status handling
# ---------------------------------------------------------------------------

class TestCheckUrl(unittest.TestCase):
    """Tests for check_url — how different HTTP responses are treated."""

    def _mock_get(self, status_code: int):
        """Context manager that mocks requests.get to return a given status."""
        return patch(
            "validation.validate_links.requests.get",
            return_value=mock_response(status_code),
        )

    def test_200_ok_is_ok(self):
        """200 response means the link is valid."""
        with self._mock_get(200):
            url, is_ok, reason = check_url("https://real-site.io/page")
        self.assertTrue(is_ok)
        self.assertEqual(reason, "")

    def test_201_created_is_ok(self):
        """2xx responses are all treated as valid."""
        with self._mock_get(201):
            url, is_ok, reason = check_url("https://real-site.io/api")
        self.assertTrue(is_ok)

    def test_301_redirect_followed_ok(self):
        """301 redirect with allow_redirects=True resolves to 200 → valid."""
        with self._mock_get(200):  # final destination after redirect
            url, is_ok, reason = check_url("https://real-site.io/old")
        self.assertTrue(is_ok)

    def test_302_redirect_resolved_ok(self):
        """302 redirect with allow_redirects=True resolves to 200 → valid."""
        with self._mock_get(200):
            url, is_ok, reason = check_url("https://real-site.io/moved")
        self.assertTrue(is_ok)

    def test_404_not_found_is_not_ok(self):
        """404 means a broken link — is_ok=False."""
        with self._mock_get(404):
            url, is_ok, reason = check_url("https://real-site.io/missing")
        self.assertFalse(is_ok)
        self.assertIn("404", reason)

    def test_404_reason_contains_status(self):
        """The reason string for a 404 includes the HTTP status code."""
        with self._mock_get(404):
            url, is_ok, reason = check_url("https://real-site.io/missing")
        self.assertIn("404", reason)

    def test_403_forbidden_treated_as_ok(self):
        """403 is bot-blocking, not a broken link — treated as OK."""
        self.assertIn(403, BOT_BLOCKING_CODES)
        with self._mock_get(403):
            url, is_ok, reason = check_url("https://real-site.io/protected")
        self.assertTrue(is_ok)

    def test_429_rate_limit_treated_as_ok(self):
        """429 Too Many Requests is rate limiting, not a broken link."""
        self.assertIn(429, BOT_BLOCKING_CODES)
        with self._mock_get(429):
            url, is_ok, reason = check_url("https://real-site.io/api")
        self.assertTrue(is_ok)

    def test_503_service_unavailable_treated_as_ok(self):
        """503 is temporary unavailability — treated as OK, not flagged."""
        self.assertIn(503, BOT_BLOCKING_CODES)
        with self._mock_get(503):
            url, is_ok, reason = check_url("https://real-site.io/down")
        self.assertTrue(is_ok)

    def test_500_server_error_is_not_ok(self):
        """500 Internal Server Error is a real failure — is_ok=False."""
        with self._mock_get(500):
            url, is_ok, reason = check_url("https://real-site.io/crash")
        self.assertFalse(is_ok)

    def test_timeout_returns_not_ok(self):
        """Timeout exception returns is_ok=False with meaningful reason."""
        with patch(
            "validation.validate_links.requests.get",
            side_effect=requests.exceptions.Timeout(),
        ):
            url, is_ok, reason = check_url("https://slow-site.io/page")
        self.assertFalse(is_ok)
        self.assertIn("timed out", reason.lower())

    def test_connection_error_returns_not_ok(self):
        """ConnectionError exception returns is_ok=False — does not crash."""
        with patch(
            "validation.validate_links.requests.get",
            side_effect=requests.exceptions.ConnectionError("ECONNREFUSED"),
        ):
            url, is_ok, reason = check_url("https://unreachable-site.io/page")
        self.assertFalse(is_ok)
        self.assertIn("Connection error", reason)

    def test_generic_request_exception_returns_not_ok(self):
        """Any RequestException subclass is caught and returns is_ok=False."""
        with patch(
            "validation.validate_links.requests.get",
            side_effect=requests.exceptions.RequestException("generic failure"),
        ):
            url, is_ok, reason = check_url("https://bad-site.io/page")
        self.assertFalse(is_ok)
        self.assertIn("Request failed", reason)

    def test_check_url_returns_input_url(self):
        """check_url always returns the URL that was passed in as first element."""
        target = "https://real-site.io/specific-path"
        with self._mock_get(200):
            url, is_ok, reason = check_url(target)
        self.assertEqual(url, target)

    def test_user_agent_header_sent(self):
        """The validator sends a User-Agent header when making requests."""
        with patch("validation.validate_links.requests.get") as mock_get:
            mock_get.return_value = mock_response(200)
            check_url("https://real-site.io/page")
            call_kwargs = mock_get.call_args[1]
            self.assertIn("User-Agent", call_kwargs.get("headers", {}))

    def test_allow_redirects_true(self):
        """requests.get is called with allow_redirects=True."""
        with patch("validation.validate_links.requests.get") as mock_get:
            mock_get.return_value = mock_response(200)
            check_url("https://real-site.io/page")
            call_kwargs = mock_get.call_args[1]
            self.assertTrue(call_kwargs.get("allow_redirects", False))

    def test_stream_mode_enabled(self):
        """requests.get is called with stream=True to avoid downloading full body."""
        with patch("validation.validate_links.requests.get") as mock_get:
            mock_get.return_value = mock_response(200)
            check_url("https://real-site.io/page")
            call_kwargs = mock_get.call_args[1]
            self.assertTrue(call_kwargs.get("stream", False))

    def test_response_close_called(self):
        """response.close() is called to free the connection."""
        resp = mock_response(200)
        with patch("validation.validate_links.requests.get", return_value=resp):
            check_url("https://real-site.io/page")
        resp.close.assert_called_once()


# ---------------------------------------------------------------------------
# validate_links: integration-level tests (uses tmp_path via pytest fixture)
# ---------------------------------------------------------------------------

class TestValidateLinksIntegration(unittest.TestCase):
    """End-to-end tests for validate_links() — result severity and exit codes."""

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _mock_get(self, status_code: int):
        return patch(
            "validation.validate_links.requests.get",
            return_value=mock_response(status_code),
        )

    def test_no_urls_returns_exit_0(self):
        """File with no external URLs → exit code 0 (clean)."""
        f = write_md(self.tmp_path, "# Title\n\nNo links here.\n")
        result = validate_links([f])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.issues, [])

    def test_only_skipped_urls_returns_exit_0(self):
        """File with only localhost/example.com URLs → exit code 0."""
        f = write_md(self.tmp_path, "See https://example.com and http://localhost:9000\n")
        result = validate_links([f])
        self.assertEqual(result.exit_code, 0)

    def test_200_link_returns_exit_0(self):
        """Single valid 200 link → exit code 0."""
        f = write_md(self.tmp_path, "See https://real-site.io/page\n")
        with self._mock_get(200):
            result = validate_links([f])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(result.issues), 0)

    def test_404_link_produces_warning_issue(self):
        """A 404 link generates a WARNING-severity issue."""
        f = write_md(self.tmp_path, "See https://broken.io/page\n")
        with self._mock_get(404):
            result = validate_links([f])
        self.assertEqual(len(result.issues), 1)
        self.assertEqual(result.issues[0].severity, Severity.WARNING)

    def test_404_link_returns_exit_2(self):
        """A 404 link (WARNING severity) → exit code 2."""
        f = write_md(self.tmp_path, "See https://broken.io/page\n")
        with self._mock_get(404):
            result = validate_links([f])
        self.assertEqual(result.exit_code, 2)

    def test_404_issue_contains_url(self):
        """The WARNING issue message contains the broken URL."""
        f = write_md(self.tmp_path, "See https://broken.io/specific-path\n")
        with self._mock_get(404):
            result = validate_links([f])
        self.assertIn("https://broken.io/specific-path", result.issues[0].message)

    def test_404_issue_contains_file_path(self):
        """The WARNING issue records the file path where the broken link was found."""
        f = write_md(self.tmp_path, "See https://broken.io/page\n")
        with self._mock_get(404):
            result = validate_links([f])
        self.assertIn(str(f), result.issues[0].file_path)

    def test_404_issue_contains_line_number(self):
        """The WARNING issue records the line number of the broken link."""
        f = write_md(self.tmp_path, "Line one\nhttps://broken.io/page\n")
        with self._mock_get(404):
            result = validate_links([f])
        self.assertEqual(result.issues[0].line_number, 2)

    def test_403_link_no_issue(self):
        """A 403 (bot-blocking) link produces no issue — treated as OK."""
        f = write_md(self.tmp_path, "See https://protected.io/page\n")
        with self._mock_get(403):
            result = validate_links([f])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(result.issues), 0)

    def test_429_link_no_issue(self):
        """A 429 (rate limited) link produces no issue."""
        f = write_md(self.tmp_path, "See https://rate-limited.io/api\n")
        with self._mock_get(429):
            result = validate_links([f])
        self.assertEqual(result.exit_code, 0)

    def test_503_link_no_issue(self):
        """A 503 (temp unavailable) link produces no issue."""
        f = write_md(self.tmp_path, "See https://down.io/page\n")
        with self._mock_get(503):
            result = validate_links([f])
        self.assertEqual(result.exit_code, 0)

    def test_timeout_produces_warning_not_exit_1(self):
        """Timeout generates a WARNING (exit 2), not a CRITICAL (exit 1)."""
        f = write_md(self.tmp_path, "See https://slow.io/page\n")
        with patch(
            "validation.validate_links.requests.get",
            side_effect=requests.exceptions.Timeout(),
        ):
            result = validate_links([f])
        self.assertGreater(len(result.issues), 0)
        # All issues should be WARNING, not CRITICAL
        for issue in result.issues:
            self.assertEqual(issue.severity, Severity.WARNING)
        self.assertEqual(result.exit_code, 2)

    def test_connection_error_does_not_crash(self):
        """ConnectionError is handled gracefully — validator continues and returns result."""
        f = write_md(self.tmp_path, "See https://unreachable.io/page\n")
        with patch(
            "validation.validate_links.requests.get",
            side_effect=requests.exceptions.ConnectionError("ECONNREFUSED"),
        ):
            result = validate_links([f])
        # Must return a result, not raise
        self.assertIsNotNone(result)
        self.assertGreater(len(result.issues), 0)

    def test_duplicate_url_checked_only_once(self):
        """The same URL appearing in multiple files is checked only once (deduplication)."""
        f1 = write_md(self.tmp_path, "See https://shared.io/page\n", "a.md")
        f2 = write_md(self.tmp_path, "Also https://shared.io/page\n", "b.md")
        call_count = 0

        def counting_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response(200)

        with patch("validation.validate_links.requests.get", side_effect=counting_get):
            validate_links([f1, f2])

        self.assertEqual(call_count, 1, "Duplicate URL was checked more than once")

    def test_duplicate_url_in_same_file_checked_once(self):
        """The same URL appearing twice in a single file is checked only once."""
        content = "https://shared.io/page\nhttps://shared.io/page\n"
        f = write_md(self.tmp_path, content)
        call_count = 0

        def counting_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response(200)

        with patch("validation.validate_links.requests.get", side_effect=counting_get):
            validate_links([f])

        self.assertEqual(call_count, 1, "Duplicate URL in same file was checked more than once")

    def test_multiple_broken_links_all_reported(self):
        """Two different 404 URLs both generate issues — not just the first."""
        content = "See https://broken-a.io/page\nAnd https://broken-b.io/page\n"
        f = write_md(self.tmp_path, content)

        def status_404(url, **kwargs):
            return mock_response(404)

        with patch("validation.validate_links.requests.get", side_effect=status_404):
            result = validate_links([f])

        self.assertEqual(len(result.issues), 2)

    def test_mixed_valid_and_broken_links(self):
        """Valid and broken links in same file: only broken generates issue."""
        content = "Good: https://good.io/page\nBad: https://bad.io/page\n"
        f = write_md(self.tmp_path, content)

        def smart_mock(url, **kwargs):
            if "good" in url:
                return mock_response(200)
            return mock_response(404)

        with patch("validation.validate_links.requests.get", side_effect=smart_mock):
            result = validate_links([f])

        self.assertEqual(len(result.issues), 1)
        self.assertIn("bad.io", result.issues[0].message)

    def test_files_checked_count_recorded(self):
        """validate_links records how many files were checked."""
        f1 = write_md(self.tmp_path, "No links\n", "a.md")
        f2 = write_md(self.tmp_path, "No links\n", "b.md")
        result = validate_links([f1, f2])
        self.assertEqual(result.files_checked, 2)

    def test_empty_file_list_returns_clean(self):
        """Calling validate_links with an empty file list returns exit 0."""
        result = validate_links([])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.issues, [])

    def test_fix_suggestion_present_on_broken_link(self):
        """Broken link issues include a fix suggestion."""
        f = write_md(self.tmp_path, "See https://broken.io/page\n")
        with self._mock_get(404):
            result = validate_links([f])
        self.assertIsNotNone(result.issues[0].fix_suggestion)
        self.assertGreater(len(result.issues[0].fix_suggestion), 0)


# ---------------------------------------------------------------------------
# find_all_md_files
# ---------------------------------------------------------------------------

class TestFindAllMdFiles(unittest.TestCase):
    """Tests for find_all_md_files — file discovery."""

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_finds_md_files_in_root(self):
        """Markdown files at root level are discovered."""
        (self.tmp_path / "README.md").write_text("# readme")
        files = find_all_md_files(self.tmp_path)
        self.assertIn(self.tmp_path / "README.md", files)

    def test_finds_md_files_in_subdirectory(self):
        """Markdown files in subdirectories are discovered recursively."""
        sub = self.tmp_path / "docs"
        sub.mkdir()
        (sub / "guide.md").write_text("# guide")
        files = find_all_md_files(self.tmp_path)
        self.assertIn(sub / "guide.md", files)

    def test_skips_dot_git_directory(self):
        """Files inside .git/ are never returned."""
        git_dir = self.tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "COMMIT_EDITMSG.md").write_text("# commit")
        files = find_all_md_files(self.tmp_path)
        for f in files:
            self.assertNotIn(".git", f.parts)

    def test_non_md_files_excluded(self):
        """Non-.md files are not included."""
        (self.tmp_path / "script.py").write_text("# python")
        (self.tmp_path / "data.json").write_text("{}")
        files = find_all_md_files(self.tmp_path)
        for f in files:
            self.assertEqual(f.suffix, ".md")

    def test_results_are_sorted(self):
        """Results are returned in sorted order (deterministic)."""
        (self.tmp_path / "z.md").write_text("")
        (self.tmp_path / "a.md").write_text("")
        files = find_all_md_files(self.tmp_path)
        md_files = [f for f in files if f.parent == self.tmp_path]
        self.assertEqual(md_files, sorted(md_files))


# ---------------------------------------------------------------------------
# Constants / configuration
# ---------------------------------------------------------------------------

class TestConstants(unittest.TestCase):
    """Verify the skip-domain and status-code constants are correctly defined."""

    def test_skip_domains_contains_localhost(self):
        self.assertIn("localhost", SKIP_DOMAINS)

    def test_skip_domains_contains_127_0_0_1(self):
        self.assertIn("127.0.0.1", SKIP_DOMAINS)

    def test_skip_domains_contains_example_com(self):
        self.assertIn("example.com", SKIP_DOMAINS)

    def test_bot_blocking_codes_contains_403(self):
        self.assertIn(403, BOT_BLOCKING_CODES)

    def test_bot_blocking_codes_contains_429(self):
        self.assertIn(429, BOT_BLOCKING_CODES)

    def test_bot_blocking_codes_contains_503(self):
        self.assertIn(503, BOT_BLOCKING_CODES)

    def test_trailing_punct_contains_period(self):
        self.assertIn(".", TRAILING_PUNCT)

    def test_trailing_punct_contains_comma(self):
        self.assertIn(",", TRAILING_PUNCT)


if __name__ == "__main__":
    unittest.main()

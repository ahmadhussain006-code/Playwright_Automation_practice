"""
conftest.py  (root level)
──────────────────────────
Pytest configuration & shared fixtures for the entire test suite.

What lives here:
  • CLI option to choose browser (--browser-name)
  • ``browser_context_args`` fixture – sets viewport, slow-mo, etc.
  • ``page`` fixture – creates a browser page, yields it, captures a
    screenshot on failure, then tears down
  • ``html_report_path`` fixture – builds a per-browser HTML report path
  • Hooks: pytest_configure, pytest_runtest_makereport

The pytest-playwright plugin registers ``playwright``, ``browser_type``,
``browser``, and ``context`` fixtures automatically – we build on top of those.
"""

import os
import pytest

from utils.helpers import capture_screenshot
from utils.logger import get_logger

logger = get_logger("conftest")


# ─────────────────────────────────────────────────────────────────────────────
# pytest_configure hook – creates required output directories early
# ─────────────────────────────────────────────────────────────────────────────

def pytest_configure(config):
    """Create output directories before the first test runs."""
    os.makedirs("reports", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    logger.info("Output directories ready: reports/ and screenshots/")


# ─────────────────────────────────────────────────────────────────────────────
# Add a custom --browser-name CLI option so we can run per-browser from CI
# ─────────────────────────────────────────────────────────────────────────────

def pytest_addoption(parser):
    """
    pytest-playwright already registers --browser, but we expose a convenience
    alias ``--browser-name`` that our GitHub Actions matrix passes in.
    """
    parser.addoption(
        "--browser-name",
        action="store",
        default=None,
        help="Override browser for this run: chromium | firefox | webkit",
    )


# ─────────────────────────────────────────────────────────────────────────────
# browser_context_args fixture – shared browser context settings
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Extend the default browser-context arguments provided by pytest-playwright.

    Sets:
      • viewport size  – 1366×768 (common laptop resolution)
      • ignore_https_errors – avoids failures on self-signed certs
      • record_video_dir – (commented out; enable if you want video artifacts)
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1366, "height": 768},
        "ignore_https_errors": True,
        # "record_video_dir": "reports/videos/",  # ← uncomment to record
    }


# ─────────────────────────────────────────────────────────────────────────────
# page fixture – with automatic screenshot on failure
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def page(context, request):
    """
    Provide a Playwright Page object and capture a screenshot if the test fails.

    Playwright's ``context`` fixture (provided by pytest-playwright) creates
    a fresh BrowserContext per test – so each test starts with clean cookies
    and storage (no cross-test contamination).

    Yield:
        playwright.sync_api.Page
    """
    page = context.new_page()
    yield page

    # ── Teardown ──────────────────────────────────────────────────────────────
    # Check if the test that used this page fixture failed
    # ``request.node`` is the test item; we inspect the call phase report
    # that was attached by the hook below.
    report = getattr(request.node, "_playwright_report", None)
    if report and report.failed:
        browser_name = request.node.callargs.get("browser_name", "unknown") \
            if hasattr(request.node, "callargs") else "unknown"
        # Fallback: read from the pytest-playwright browser fixture value
        try:
            browser_name = page.context.browser.browser_type.name
        except Exception:
            pass

        screenshot_path = capture_screenshot(
            page, request.node.nodeid, browser_name
        )
        logger.warning("Test FAILED – screenshot saved to %s", screenshot_path)

        # Attach screenshot to the HTML report (pytest-html extra)
        extras = getattr(report, "extras", [])
        try:
            from pytest_html import extras as html_extras  # type: ignore
            extras.append(html_extras.image(screenshot_path))
            report.extras = extras
        except ImportError:
            pass  # pytest-html not installed – skip attachment

    page.close()


# ─────────────────────────────────────────────────────────────────────────────
# Hook: attach report object to the test node for use in the page fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    After each test phase (setup / call / teardown), attach the report to the
    test node so the ``page`` fixture can check whether the test failed.
    """
    outcome = yield
    report = outcome.get_result()

    # We only care about the test body phase (not setup/teardown)
    if call.when == "call":
        item._playwright_report = report


# ─────────────────────────────────────────────────────────────────────────────
# html_report_path fixture – per-browser report file path
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def html_report_path(request):
    """
    Return the path where the HTML report for this session should be written.

    pytest-html is configured via the ``--html`` CLI option; this fixture
    exposes the path so tests can log it.
    """
    return request.config.getoption("--html", default="reports/report.html")
"""
conftest.py  (root level)
──────────────────────────
Pytest configuration and shared fixtures.

Key fix (v4):
  The previous version defined a custom `page` fixture that conflicted
  with pytest-playwright's built-in `page` fixture on Firefox and WebKit,
  causing "BrowserContext.new_page: Target page, context or browser has
  been closed" errors.

  Fix: Remove the custom page fixture entirely.
  pytest-playwright manages the browser/context/page lifecycle correctly.
  Screenshot-on-failure is handled via pytest_runtest_makereport hook
  using the `request` object inside the test, NOT by wrapping the page fixture.
"""

import os
import pytest

from utils.logger import get_logger

logger = get_logger("conftest")


# ─────────────────────────────────────────────────────────────────────────────
# pytest_configure – create output folders before the first test
# ─────────────────────────────────────────────────────────────────────────────

def pytest_configure(config):
    """Create output directories before any test runs."""
    os.makedirs("reports", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    logger.info("Output directories ready: reports/ and screenshots/")


# ─────────────────────────────────────────────────────────────────────────────
# browser_context_args – shared viewport / context settings
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Extend pytest-playwright's default browser context arguments.
    Sets viewport to a standard laptop resolution and ignores HTTPS errors.
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1366, "height": 768},
        "ignore_https_errors": True,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Hook: capture screenshot on test failure
# ─────────────────────────────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    After the test CALL phase, if the test failed:
      1. Capture a full-page screenshot using the `page` fixture value
      2. Attach it to the HTML report via pytest-html extras
      3. Log the screenshot path

    This approach does NOT wrap the page fixture, so it is fully compatible
    with pytest-playwright's internal browser/context/page lifecycle on all
    three browsers (Chromium, Firefox, WebKit).
    """
    outcome = yield
    report = outcome.get_result()

    # Only act on the test body phase (not setup/teardown)
    if call.when == "call" and report.failed:

        # Get the `page` object from the test's fixture values
        page = item.funcargs.get("page")
        if page is None:
            return

        # Build a safe filename
        from datetime import datetime
        browser_name = "unknown"
        try:
            browser_name = page.context.browser.browser_type.name
        except Exception:
            pass

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
        screenshot_path = f"screenshots/{browser_name}_{safe_name}_{timestamp}.png"

        # Take screenshot
        try:
            page.screenshot(path=screenshot_path, full_page=True)
            logger.warning("Test FAILED – screenshot saved to %s", screenshot_path)
        except Exception as e:
            logger.error("Could not capture screenshot: %s", e)
            return

        # Attach to pytest-html report
        try:
            from pytest_html import extras as html_extras
            extra = getattr(report, "extras", [])
            extra.append(html_extras.image(screenshot_path))
            report.extras = extra
        except Exception:
            pass  # pytest-html not installed or extras unavailable
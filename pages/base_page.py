"""
pages/base_page.py
──────────────────
Base Page Object – every other page class inherits from this.

Provides:
  • A shared Playwright page instance
  • Wrappers around common Playwright actions (navigate, click, fill, etc.)
  • Built-in waits so individual page objects don't repeat boilerplate
  • Logging for every interaction

Timeout strategy:
  Chromium is fast → 15 s is fine locally
  Firefox / WebKit in headless CI are slower → we read an env var
  PLAYWRIGHT_TIMEOUT (set in the workflow) and fall back to 30 s.
  This means you can tune timeouts per-browser in CI without changing code.
"""

import os
from playwright.sync_api import Page, expect
from utils.logger import get_logger


class BasePage:
    """
    Parent class for all Page Object classes.
    """

    # Read timeout from env var (set in GitHub Actions workflow per browser).
    # Default = 30 000 ms (30 s) – generous enough for Firefox/WebKit in CI.
    DEFAULT_TIMEOUT = int(os.environ.get("PLAYWRIGHT_TIMEOUT", "30000"))

    def __init__(self, page: Page) -> None:
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, url: str) -> None:
        """Open the given URL and wait until the DOM is ready."""
        self.logger.info("Navigating to: %s", url)
        self.page.goto(url, wait_until="domcontentloaded")

    # ── Element interactions ──────────────────────────────────────────────────

    def click(self, selector: str) -> None:
        """Wait for an element to be visible then click it."""
        self.logger.debug("Clicking: %s", selector)
        self.page.locator(selector).wait_for(
            state="visible", timeout=self.DEFAULT_TIMEOUT
        )
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str) -> None:
        """Clear a text field and type the given value."""
        self.logger.debug("Filling '%s' with: %s", selector, value)
        self.page.locator(selector).wait_for(
            state="visible", timeout=self.DEFAULT_TIMEOUT
        )
        self.page.locator(selector).fill(value)

    def select_option(self, selector: str, value: str) -> None:
        """Select a <select> dropdown option by its value attribute."""
        self.logger.debug("Selecting '%s' in: %s", value, selector)
        self.page.locator(selector).select_option(value)

    def check_checkbox(self, selector: str) -> None:
        """Tick a checkbox (no-op if already checked)."""
        self.logger.debug("Checking checkbox: %s", selector)
        locator = self.page.locator(selector)
        if not locator.is_checked():
            locator.check()

    def get_text(self, selector: str) -> str:
        """Return the trimmed inner text of a visible element."""
        self.page.locator(selector).wait_for(
            state="visible", timeout=self.DEFAULT_TIMEOUT
        )
        text = self.page.locator(selector).inner_text().strip()
        self.logger.debug("Text at '%s': %s", selector, text)
        return text

    def is_visible(self, selector: str) -> bool:
        """Return True if the element is currently visible in the viewport."""
        try:
            self.page.locator(selector).wait_for(
                state="visible", timeout=self.DEFAULT_TIMEOUT
            )
            return True
        except Exception:
            return False

    # ── Assertion helpers ─────────────────────────────────────────────────────

    def assert_text_visible(self, selector: str, expected_text: str) -> None:
        """Assert that the element contains the expected text."""
        self.logger.info(
            "Asserting text '%s' is visible in '%s'", expected_text, selector
        )
        expect(self.page.locator(selector)).to_contain_text(
            expected_text, ignore_case=True, timeout=self.DEFAULT_TIMEOUT
        )

    def assert_url_contains(self, fragment: str) -> None:
        """Assert that the current URL contains the given fragment."""
        self.logger.info("Asserting URL contains: %s", fragment)
        assert fragment in self.page.url, (
            f"Expected URL to contain '{fragment}' but got '{self.page.url}'"
        )
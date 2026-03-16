"""
pages/home_page.py
──────────────────
Page Object for the AutomationExercise **Home Page**.

Responsibilities:
  • Verify the home page loaded correctly
  • Click the Signup / Login navigation link
"""

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class HomePage(BasePage):
    """Represents https://automationexercise.com (the landing page)."""

    # ── Selectors ─────────────────────────────────────────────────────────────
    # Using CSS selectors.  Keep selectors here so a UI change only needs
    # a one-line fix in this file, not across every test.

    LOGO = "img[src='/static/images/home/logo.png']"   # top-left site logo
    NAV_SIGNUP_LOGIN = "a[href='/login']"               # "Signup / Login" nav item
    BODY = "body"                                        # used to assert page load

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ── Actions ───────────────────────────────────────────────────────────────

    def open(self) -> None:
        """Navigate to the home page."""
        self.navigate("https://automationexercise.com")

    def click_signup_login(self) -> None:
        """Click the 'Signup / Login' link in the top navigation bar."""
        self.logger.info("Clicking 'Signup / Login' nav link")
        self.click(self.NAV_SIGNUP_LOGIN)

    # ── Assertions ────────────────────────────────────────────────────────────

    def verify_home_page_is_visible(self) -> None:
        """
        Verify the home page loaded successfully.

        Checks:
          1. The page title contains 'Automation Exercise'
          2. The site logo is visible
        """
        self.logger.info("Verifying home page is visible")

        # 1. Title check
        expect(self.page).to_have_title(
            "Automation Exercise", timeout=self.DEFAULT_TIMEOUT
        )
        self.logger.info("✔ Page title verified: 'Automation Exercise'")

        # 2. Logo visibility
        expect(self.page.locator(self.LOGO)).to_be_visible(
            timeout=self.DEFAULT_TIMEOUT
        )
        self.logger.info("✔ Site logo is visible – home page loaded correctly")
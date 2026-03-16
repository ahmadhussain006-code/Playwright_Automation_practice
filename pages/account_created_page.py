"""
pages/account_created_page.py
──────────────────────────────
Page Object for the Account Created confirmation page and the
subsequent logged-in home page check.

URL: https://automationexercise.com/account_created

Fixes applied (v2):
  - Added wait_for_url() after Create Account so CI (headless/fast)
    does not assert before the page has navigated
  - Selector uses :has-text() directly instead of a nested <b> tag
    so it works regardless of the exact DOM structure
  - Fallback: also checks the paragraph text if the heading is absent
"""

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class AccountCreatedPage(BasePage):
    """
    Represents the confirmation page shown after a successful registration.
    Works in both headed (local) and headless (CI) modes.
    """

    # ── Selectors ─────────────────────────────────────────────────────────────

    # Primary: the <h2> heading that contains "ACCOUNT CREATED!"
    # Using :has-text() so we don't depend on a nested <b> tag
    ACCOUNT_CREATED_HEADING = "h2:has-text('Account Created')"

    # Fallback: the confirmation paragraph also contains the success text
    ACCOUNT_CREATED_PARAGRAPH = "p:has-text('Congratulations')"

    # 'Continue' button
    CONTINUE_BUTTON = "a[data-qa='continue-button']"

    # Nav-bar "Logged in as <username>" link
    LOGGED_IN_AS = "a:has-text('Logged in as')"

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ── Assertions ────────────────────────────────────────────────────────────

    def verify_account_created(self) -> None:
        """
        Assert the 'Account Created!' confirmation is displayed.

        Strategy (most-to-least specific):
          1. Wait for the URL to contain /account_created   ← catches slow CI
          2. Assert the heading is visible
          3. If heading not found, assert the paragraph text (fallback)
        """
        self.logger.info("Verifying 'ACCOUNT CREATED!' message is visible")

        # ── Step 1: wait for navigation to the confirmation URL ───────────────
        # This is the key fix for CI – we don't assert until the browser has
        # actually navigated away from the registration form.
        try:
            self.page.wait_for_url(
                "**/account_created**",
                timeout=20_000,      # 20 s – generous for slow CI runners
                wait_until="domcontentloaded",
            )
            self.logger.info("✔ URL contains /account_created – page navigation confirmed")
        except Exception:
            # URL pattern didn't match – log a warning but keep trying
            self.logger.warning(
                "wait_for_url('/account_created') timed out – "
                "current URL: %s  – continuing with element check",
                self.page.url,
            )

        # ── Step 2: assert heading is visible ─────────────────────────────────
        try:
            expect(
                self.page.locator(self.ACCOUNT_CREATED_HEADING).first
            ).to_be_visible(timeout=self.DEFAULT_TIMEOUT)
            self.logger.info("✔ 'ACCOUNT CREATED!' heading confirmed")

        except Exception:
            # ── Step 3: fallback – check the paragraph ────────────────────────
            self.logger.warning(
                "Heading selector not found – trying paragraph fallback"
            )
            expect(
                self.page.locator(self.ACCOUNT_CREATED_PARAGRAPH).first
            ).to_be_visible(timeout=self.DEFAULT_TIMEOUT)
            self.logger.info("✔ 'ACCOUNT CREATED!' confirmed via paragraph fallback")

    def verify_logged_in_as(self, username: str) -> None:
        """
        Assert the nav bar shows 'Logged in as <username>'.

        Args:
            username: The first name used at registration (e.g. 'Ahmad').
        """
        self.logger.info("Verifying 'Logged in as %s' is visible", username)

        # Wait for home page to fully load after Continue click
        self.page.wait_for_load_state("domcontentloaded")

        locator = self.page.locator(self.LOGGED_IN_AS)
        expect(locator).to_be_visible(timeout=self.DEFAULT_TIMEOUT)
        expect(locator).to_contain_text(username, ignore_case=True,
                                        timeout=self.DEFAULT_TIMEOUT)
        self.logger.info("✔ 'Logged in as %s' confirmed in nav bar", username)

    # ── Actions ───────────────────────────────────────────────────────────────

    def click_continue(self) -> None:
        """Click the 'Continue' button to return to the home page."""
        self.logger.info("Clicking 'Continue' button")
        self.click(self.CONTINUE_BUTTON)
        # Wait for home page load after redirect
        self.page.wait_for_load_state("domcontentloaded")
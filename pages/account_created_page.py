"""
pages/account_created_page.py
──────────────────────────────
Page Object for the **Account Created** confirmation page and the
subsequent **logged-in home page** check.

URL: https://automationexercise.com/account_created

Responsibilities:
  • Verify 'ACCOUNT CREATED!' message
  • Click the 'Continue' button
  • Verify the 'Logged in as <username>' indicator in the nav bar
"""

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class AccountCreatedPage(BasePage):
    """
    Represents the confirmation page shown after a successful registration.
    """

    # ── Selectors ─────────────────────────────────────────────────────────────

    # The big heading displayed on the account-created confirmation page
    ACCOUNT_CREATED_HEADING = "h2[data-qa='account-created'] b"

    # 'Continue' button that takes the user back to the home page (logged in)
    CONTINUE_BUTTON = "a[data-qa='continue-button']"

    # Nav-bar element that shows "Logged in as <username>"
    # The selector targets the <li> that contains the user-icon link
    LOGGED_IN_AS = "a:has-text('Logged in as')"

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ── Assertions ────────────────────────────────────────────────────────────

    def verify_account_created(self) -> None:
        """Assert that the 'ACCOUNT CREATED!' heading is visible."""
        self.logger.info("Verifying 'ACCOUNT CREATED!' message is visible")
        expect(
            self.page.locator(self.ACCOUNT_CREATED_HEADING)
        ).to_contain_text("ACCOUNT CREATED!", ignore_case=True,
                           timeout=self.DEFAULT_TIMEOUT)
        self.logger.info("✔ 'ACCOUNT CREATED!' confirmed")

    def verify_logged_in_as(self, username: str) -> None:
        """
        Assert that the nav bar shows 'Logged in as <username>'.

        Args:
            username: The first name / display name used at registration.
        """
        self.logger.info("Verifying 'Logged in as %s' is visible", username)
        locator = self.page.locator(self.LOGGED_IN_AS)
        expect(locator).to_be_visible(timeout=self.DEFAULT_TIMEOUT)
        # Also verify the actual username appears in the link text
        expect(locator).to_contain_text(username, ignore_case=True,
                                         timeout=self.DEFAULT_TIMEOUT)
        self.logger.info("✔ 'Logged in as %s' confirmed in nav bar", username)

    # ── Actions ───────────────────────────────────────────────────────────────

    def click_continue(self) -> None:
        """Click the 'Continue' button to return to the home page."""
        self.logger.info("Clicking 'Continue' button")
        self.click(self.CONTINUE_BUTTON)
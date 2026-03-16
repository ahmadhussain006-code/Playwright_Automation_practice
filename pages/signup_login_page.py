"""
pages/signup_login_page.py
──────────────────────────
Page Object for the AutomationExercise **Signup / Login** page.

URL: https://automationexercise.com/login

Responsibilities:
  • Verify the 'New User Signup!' section is visible
  • Fill in name + email and click the Signup button
"""

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SignupLoginPage(BasePage):
    """
    Represents the combined Signup / Login page.

    The page has two sections:
      - Left:  Login with existing credentials
      - Right: 'New User Signup!' form
    """

    # ── Selectors ─────────────────────────────────────────────────────────────

    # Heading that confirms we are on the signup section
    NEW_USER_SIGNUP_HEADING = "h2:has-text('New User Signup!')"

    # Signup form fields
    SIGNUP_NAME_INPUT  = "input[data-qa='signup-name']"
    SIGNUP_EMAIL_INPUT = "input[data-qa='signup-email']"
    SIGNUP_BUTTON      = "button[data-qa='signup-button']"

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ── Assertions ────────────────────────────────────────────────────────────

    def verify_new_user_signup_visible(self) -> None:
        """Assert that the 'New User Signup!' heading is visible."""
        self.logger.info("Verifying 'New User Signup!' section is visible")
        expect(
            self.page.locator(self.NEW_USER_SIGNUP_HEADING)
        ).to_be_visible(timeout=self.DEFAULT_TIMEOUT)
        self.logger.info("✔ 'New User Signup!' heading is visible")

    # ── Actions ───────────────────────────────────────────────────────────────

    def enter_signup_name(self, name: str) -> None:
        """Type the user's name into the signup name field."""
        self.logger.info("Entering signup name: %s", name)
        self.fill(self.SIGNUP_NAME_INPUT, name)

    def enter_signup_email(self, email: str) -> None:
        """Type the user's email into the signup email field."""
        self.logger.info("Entering signup email: %s", email)
        self.fill(self.SIGNUP_EMAIL_INPUT, email)

    def click_signup_button(self) -> None:
        """Click the 'Signup' button to proceed to account registration."""
        self.logger.info("Clicking 'Signup' button")
        self.click(self.SIGNUP_BUTTON)

    # ── Convenience composite method ─────────────────────────────────────────

    def signup_new_user(self, name: str, email: str) -> None:
        """
        Complete the full new-user signup entry in one call.

        Verifies the heading, fills name + email, then clicks Signup.
        """
        self.verify_new_user_signup_visible()
        self.enter_signup_name(name)
        self.enter_signup_email(email)
        self.click_signup_button()
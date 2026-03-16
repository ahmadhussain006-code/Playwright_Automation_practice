"""
tests/test_register_user.py
────────────────────────────
End-to-end test: Register User on https://automationexercise.com

Test scenario (all 16 steps from the specification):
  1.  Launch browser                                    ← handled by conftest
  2.  Navigate to https://automationexercise.com
  3.  Verify home page is visible
  4.  Click 'Signup / Login'
  5.  Verify 'New User Signup!' is visible
  6.  Enter name and email
  7.  Click 'Signup'
  8.  Verify 'ENTER ACCOUNT INFORMATION' is visible
  9.  Fill account details (title, password, DOB)
  10. Check 'Sign up for our newsletter'
  11. Check 'Receive special offers from our partners'
  12. Fill address details
  13. Click 'Create Account'
  14. Verify 'ACCOUNT CREATED!'
  15. Click 'Continue'
  16. Verify 'Logged in as Ahmad'
"""

import logging

import pytest

from pages.account_created_page import AccountCreatedPage
from pages.home_page import HomePage
from pages.registration_page import RegistrationPage
from pages.signup_login_page import SignupLoginPage
from utils.helpers import generate_unique_email

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Test data  –  kept here for easy reading; move to a data file / fixture
#              if you need parameterised runs with different data sets.
# ─────────────────────────────────────────────────────────────────────────────

USER_DATA = {
    "name":         "Ahmad Hussain",
    "first_name":   "Ahmad",
    "last_name":    "Hussain",
    "title":        "Mr",
    "password":     "Test@123",
    "dob":          "24/11/1991",    # DD/MM/YYYY
    "address":      "Test Street",
    "country":      "India",
    "state":        "UP",
    "city":         "Lucknow",
    "zipcode":      "226001",
    "mobile":       "9999999999",
}


# ─────────────────────────────────────────────────────────────────────────────
# Test class
# ─────────────────────────────────────────────────────────────────────────────

class TestRegisterUser:
    """
    Groups all register-user related tests.

    Each test method is independent and uses its own browser page (provided
    by the ``page`` fixture in conftest.py).
    """

    # ── Marks ─────────────────────────────────────────────────────────────────
    # All methods in this class are tagged with the 'register' and 'regression'
    # markers defined in pytest.ini.
    pytestmark = [pytest.mark.register, pytest.mark.regression]

    # ─────────────────────────────────────────────────────────────────────────

    def test_register_user(self, page) -> None:
        """
        Full Register User flow – validates every checkpoint in the spec.

        This is a single test method because the steps form a linear flow
        where each step depends on the previous one completing successfully.
        For a larger suite you might split each step into a separate test
        with shared state passed via fixtures.
        """

        # ── Generate a unique email for this specific run ─────────────────────
        unique_email = generate_unique_email("ahmad")
        logger.info("=" * 60)
        logger.info("TEST START: test_register_user")
        logger.info("Email for this run: %s", unique_email)
        logger.info("=" * 60)

        # ── Instantiate page objects ──────────────────────────────────────────
        home_page         = HomePage(page)
        signup_login_page = SignupLoginPage(page)
        registration_page = RegistrationPage(page)
        account_created   = AccountCreatedPage(page)

        # ── STEP 2: Navigate to the site ──────────────────────────────────────
        logger.info("STEP 2 – Navigate to https://automationexercise.com")
        home_page.open()

        # ── STEP 3: Verify home page ──────────────────────────────────────────
        logger.info("STEP 3 – Verify home page is visible")
        home_page.verify_home_page_is_visible()

        # ── STEP 4: Click Signup / Login ──────────────────────────────────────
        logger.info("STEP 4 – Click 'Signup / Login'")
        home_page.click_signup_login()

        # ── STEP 5: Verify 'New User Signup!' ─────────────────────────────────
        logger.info("STEP 5 – Verify 'New User Signup!' is visible")
        signup_login_page.verify_new_user_signup_visible()

        # ── STEP 6 & 7: Enter name + email then click Signup ──────────────────
        logger.info("STEP 6 – Enter name: %s  |  email: %s", USER_DATA["name"], unique_email)
        signup_login_page.enter_signup_name(USER_DATA["name"])
        signup_login_page.enter_signup_email(unique_email)

        logger.info("STEP 7 – Click 'Signup' button")
        signup_login_page.click_signup_button()

        # ── STEP 8: Verify 'ENTER ACCOUNT INFORMATION' ───────────────────────
        logger.info("STEP 8 – Verify 'ENTER ACCOUNT INFORMATION' heading")
        registration_page.verify_enter_account_information_visible()

        # ── STEPS 9–12: Fill the full registration form ───────────────────────
        logger.info("STEPS 9-12 – Fill account + address details")
        registration_page.fill_registration_form(
            password   = USER_DATA["password"],
            dob        = USER_DATA["dob"],
            first_name = USER_DATA["first_name"],
            last_name  = USER_DATA["last_name"],
            address    = USER_DATA["address"],
            country    = USER_DATA["country"],
            state      = USER_DATA["state"],
            city       = USER_DATA["city"],
            zipcode    = USER_DATA["zipcode"],
            mobile     = USER_DATA["mobile"],
            title      = USER_DATA["title"],
        )

        # ── STEP 13: Create Account button ────────────────────────────────────
        # Already clicked inside fill_registration_form() → no extra call needed

        # ── STEP 14: Verify 'ACCOUNT CREATED!' ───────────────────────────────
        logger.info("STEP 14 – Verify 'ACCOUNT CREATED!' message")
        account_created.verify_account_created()

        # ── STEP 15: Click Continue ───────────────────────────────────────────
        logger.info("STEP 15 – Click 'Continue' button")
        account_created.click_continue()

        # ── STEP 16: Verify 'Logged in as Ahmad' ─────────────────────────────
        logger.info("STEP 16 – Verify 'Logged in as %s'", USER_DATA["first_name"])
        account_created.verify_logged_in_as(USER_DATA["first_name"])

        logger.info("=" * 60)
        logger.info("TEST PASSED: test_register_user ✔")
        logger.info("=" * 60)
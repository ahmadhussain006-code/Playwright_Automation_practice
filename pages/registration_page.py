"""
pages/registration_page.py
──────────────────────────
Page Object for the AutomationExercise **Account Registration** page.

URL: https://automationexercise.com/signup  (reached after the signup form)

This page asks for:
  • Title (Mr / Mrs radio buttons)
  • Password
  • Date of Birth (three separate dropdowns)
  • Newsletter & special-offers checkboxes
  • Full address details (name, address, country, state, city, zip, phone)

Then the user clicks 'Create Account'.
"""

from playwright.sync_api import Page, expect

from pages.base_page import BasePage
from utils.helpers import parse_dob


class RegistrationPage(BasePage):
    """
    Represents the full account-registration form reached after signup.
    """

    # ── Selectors ─────────────────────────────────────────────────────────────

    # Section heading – confirms we landed on the right page.
    # The page has TWO <h2.title.text-center b> elements ("Enter Account Information"
    # AND "Address Information"), so we target the text directly to avoid a
    # strict-mode violation caused by multiple matches.
    ACCOUNT_INFO_HEADING = "h2.title.text-center b:has-text('Enter Account Information')"

    # ── Account / personal information ───────────────────────────────────────
    TITLE_MR_RADIO      = "#id_gender1"                          # Mr radio button
    TITLE_MRS_RADIO     = "#id_gender2"                          # Mrs radio button
    PASSWORD_INPUT      = "input[data-qa='password']"
    DOB_DAY_SELECT      = "select[data-qa='days']"
    DOB_MONTH_SELECT    = "select[data-qa='months']"
    DOB_YEAR_SELECT     = "select[data-qa='years']"

    # ── Opt-in checkboxes ─────────────────────────────────────────────────────
    NEWSLETTER_CHECKBOX       = "#newsletter"
    SPECIAL_OFFERS_CHECKBOX   = "#optin"

    # ── Address information ───────────────────────────────────────────────────
    FIRST_NAME_INPUT    = "input[data-qa='first_name']"
    LAST_NAME_INPUT     = "input[data-qa='last_name']"
    COMPANY_INPUT       = "input[data-qa='company']"       # optional – not filled
    ADDRESS1_INPUT      = "input[data-qa='address']"
    ADDRESS2_INPUT      = "input[data-qa='address2']"      # optional – not filled
    COUNTRY_SELECT      = "select[data-qa='country']"
    STATE_INPUT         = "input[data-qa='state']"
    CITY_INPUT          = "input[data-qa='city']"
    ZIPCODE_INPUT       = "input[data-qa='zipcode']"
    MOBILE_INPUT        = "input[data-qa='mobile_number']"

    # ── Submit ────────────────────────────────────────────────────────────────
    CREATE_ACCOUNT_BUTTON = "button[data-qa='create-account']"

    # ── Constructor ───────────────────────────────────────────────────────────

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ── Assertions ────────────────────────────────────────────────────────────

    def verify_enter_account_information_visible(self) -> None:
        """Assert the 'Enter Account Information' heading is displayed."""
        self.logger.info("Verifying 'Enter Account Information' heading is visible")
        # Selector already filters by exact text – just assert visibility to
        # avoid strict-mode violations from multiple matching elements.
        expect(
            self.page.locator(self.ACCOUNT_INFO_HEADING)
        ).to_be_visible(timeout=self.DEFAULT_TIMEOUT)
        self.logger.info("✔ 'Enter Account Information' heading verified")

    # ── Actions – Account info ────────────────────────────────────────────────

    def select_title_mr(self) -> None:
        """Select the 'Mr' title radio button."""
        self.logger.info("Selecting title: Mr")
        self.page.locator(self.TITLE_MR_RADIO).check()

    def enter_password(self, password: str) -> None:
        """Enter the account password."""
        self.logger.info("Entering password")
        self.fill(self.PASSWORD_INPUT, password)

    def select_date_of_birth(self, dob: str) -> None:
        """
        Select day / month / year from the three DOB dropdowns.

        Args:
            dob: Date string in ``DD/MM/YYYY`` format.
        """
        self.logger.info("Setting date of birth: %s", dob)
        parts = parse_dob(dob)
        self.select_option(self.DOB_DAY_SELECT,   parts["day"])
        self.select_option(self.DOB_MONTH_SELECT, parts["month"])
        self.select_option(self.DOB_YEAR_SELECT,  parts["year"])

    # ── Actions – Opt-in checkboxes ───────────────────────────────────────────

    def check_newsletter(self) -> None:
        """Tick the 'Sign up for our newsletter!' checkbox."""
        self.logger.info("Checking 'newsletter' checkbox")
        self.check_checkbox(self.NEWSLETTER_CHECKBOX)

    def check_special_offers(self) -> None:
        """Tick the 'Receive special offers from our partners!' checkbox."""
        self.logger.info("Checking 'special offers' checkbox")
        self.check_checkbox(self.SPECIAL_OFFERS_CHECKBOX)

    # ── Actions – Address info ────────────────────────────────────────────────

    def enter_first_name(self, first_name: str) -> None:
        self.logger.info("Entering first name: %s", first_name)
        self.fill(self.FIRST_NAME_INPUT, first_name)

    def enter_last_name(self, last_name: str) -> None:
        self.logger.info("Entering last name: %s", last_name)
        self.fill(self.LAST_NAME_INPUT, last_name)

    def enter_address(self, address: str) -> None:
        self.logger.info("Entering address: %s", address)
        self.fill(self.ADDRESS1_INPUT, address)

    def select_country(self, country: str) -> None:
        """Select a country from the dropdown (value must match the option text)."""
        self.logger.info("Selecting country: %s", country)
        self.select_option(self.COUNTRY_SELECT, country)

    def enter_state(self, state: str) -> None:
        self.logger.info("Entering state: %s", state)
        self.fill(self.STATE_INPUT, state)

    def enter_city(self, city: str) -> None:
        self.logger.info("Entering city: %s", city)
        self.fill(self.CITY_INPUT, city)

    def enter_zipcode(self, zipcode: str) -> None:
        self.logger.info("Entering zipcode: %s", zipcode)
        self.fill(self.ZIPCODE_INPUT, zipcode)

    def enter_mobile_number(self, mobile: str) -> None:
        self.logger.info("Entering mobile number: %s", mobile)
        self.fill(self.MOBILE_INPUT, mobile)

    # ── Actions – Submit ──────────────────────────────────────────────────────

    def click_create_account(self) -> None:
        """
        Click the 'Create Account' button and wait for navigation.

        The explicit wait_for_load_state is critical for CI (headless):
        without it, the next assertion fires before the browser has finished
        navigating to the /account_created confirmation page.
        """
        self.logger.info("Clicking 'Create Account' button")
        self.click(self.CREATE_ACCOUNT_BUTTON)
        # Wait until DOM is ready on the confirmation page
        self.page.wait_for_load_state("domcontentloaded")

    # ── Composite convenience method ──────────────────────────────────────────

    def fill_registration_form(
        self,
        password: str,
        dob: str,
        first_name: str,
        last_name: str,
        address: str,
        country: str,
        state: str,
        city: str,
        zipcode: str,
        mobile: str,
        title: str = "Mr",
    ) -> None:
        """
        Fill in the entire registration form and submit it.

        Follows the exact order the UI presents the fields (top → bottom)
        to avoid scrolling / visibility issues.
        """
        self.logger.info("Starting to fill registration form for %s %s", first_name, last_name)

        # Step 1 – Personal info
        if title == "Mr":
            self.select_title_mr()
        self.enter_password(password)
        self.select_date_of_birth(dob)

        # Step 2 – Opt-in checkboxes
        self.check_newsletter()
        self.check_special_offers()

        # Step 3 – Address details
        self.enter_first_name(first_name)
        self.enter_last_name(last_name)
        self.enter_address(address)
        self.select_country(country)
        self.enter_state(state)
        self.enter_city(city)
        self.enter_zipcode(zipcode)
        self.enter_mobile_number(mobile)

        # Step 4 – Submit
        self.click_create_account()
        self.logger.info("Registration form submitted")
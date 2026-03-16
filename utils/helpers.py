"""
utils/helpers.py
────────────────
Reusable helper functions used across tests and page objects.

Includes:
  - Unique e-mail generator
  - Screenshot capture utility
  - Date-of-birth formatter
"""

import os
from datetime import datetime

from faker import Faker

from utils.logger import get_logger

logger = get_logger(__name__)

# Seed Faker with a locale – English (India) gives realistic names & addresses
fake = Faker("en_IN")


# ─────────────────────────────────────────────────────────────────────────────
# Email helpers
# ─────────────────────────────────────────────────────────────────────────────

def generate_unique_email(prefix: str = "test") -> str:
    """
    Generate a unique e-mail address for every test run.

    Uses a timestamp + random UUID fragment to guarantee uniqueness even when
    multiple test runs overlap (e.g. parallel CI jobs).

    Args:
        prefix: Optional string prepended to the local part (default ``"test"``).

    Returns:
        A unique e-mail string, e.g. ``test_20240517_143022_a1b2@mailtest.com``.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_part = fake.uuid4()[:8]            # first 8 chars of a UUID
    email = f"{prefix}_{timestamp}_{unique_part}@mailtest.com"
    logger.debug("Generated unique email: %s", email)
    return email


# ─────────────────────────────────────────────────────────────────────────────
# Screenshot helpers
# ─────────────────────────────────────────────────────────────────────────────

def capture_screenshot(page, test_name: str, browser_name: str = "chromium") -> str:
    """
    Capture a full-page screenshot and save it to the ``screenshots/`` folder.

    The filename includes the browser name, test name, and a timestamp so
    screenshots from different browsers / runs never overwrite each other.

    Args:
        page:         Playwright ``Page`` object.
        test_name:    Name of the test (used in the filename).
        browser_name: Name of the current browser (default ``"chromium"``).

    Returns:
        The absolute path of the saved screenshot file.
    """
    os.makedirs("screenshots", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitise the test name so it is safe as a filename
    safe_test_name = test_name.replace("::", "_").replace("/", "_")
    filename = f"screenshots/{browser_name}_{safe_test_name}_{timestamp}.png"

    page.screenshot(path=filename, full_page=True)
    logger.info("📸 Screenshot saved: %s", filename)
    return filename


# ─────────────────────────────────────────────────────────────────────────────
# Date helpers
# ─────────────────────────────────────────────────────────────────────────────

def parse_dob(dob_string: str) -> dict:
    """
    Parse a date-of-birth string (``DD/MM/YYYY``) into a dict with
    separate ``day``, ``month``, and ``year`` keys – matching the
    dropdown values on the registration form.

    Args:
        dob_string: Date string in ``DD/MM/YYYY`` format, e.g. ``"24/11/1991"``.

    Returns:
        ``{"day": "24", "month": "11", "year": "1991"}``
    """
    parts = dob_string.split("/")
    if len(parts) != 3:
        raise ValueError(f"Invalid DOB format '{dob_string}'. Expected DD/MM/YYYY.")
    return {"day": parts[0], "month": parts[1], "year": parts[2]}
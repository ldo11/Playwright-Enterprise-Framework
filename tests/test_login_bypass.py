import pytest

from pages.home_page import HomePage


@pytest.mark.smoke
@pytest.mark.auth
def test_login_bypass(auth_page):
    """Verify we start in an authenticated state using storageState created via API login bypass."""
    home = HomePage(auth_page)
    home.goto()
    assert home.is_logged_in(), "Expected to be logged in via API login bypass without UI login."

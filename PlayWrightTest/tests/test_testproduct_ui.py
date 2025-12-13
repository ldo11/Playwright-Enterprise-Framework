import pytest

from pages.home_page import HomePage


@pytest.mark.ui
class TestTestProductUI:
    def test_dashboard_visible_with_pre_authenticated_state(self, auth_page):
        """Verify that with API-login-based storageState, we land on the Client List dashboard already logged in."""
        home = HomePage(auth_page)
        home.goto()
        assert home.is_logged_in(), "Expected Client List dashboard to be visible when using pre-auth storageState."

    def test_add_client_via_ui(self, auth_page):
        """Create a client via the UI and assert its first name appears as a clickable entry."""
        home = HomePage(auth_page)
        home.goto()
        assert home.is_logged_in(), "Precondition: user should be logged in."

        home.add_client("Playwright", "User", "2000-01-01", "Male")
        row = home.client_row_by_first_name("Playwright")
        row.click()

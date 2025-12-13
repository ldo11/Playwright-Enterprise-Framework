from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import APP_URL


class HomePage:
    """POM for the TestProduct Client Management dashboard (Client List)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        # Top app toolbar
        self.app_title = page.get_by_text("Client Management System")
        # Inner toolbar on the dashboard
        self.client_list_toolbar = page.get_by_text("Client List")
        self.add_client_button = page.get_by_role("button", name="Add Client")
        self.logout_button = page.get_by_role("button", name="Logout")

    def goto(self) -> None:
        """Navigate directly to the dashboard (App URL)."""
        self.page.goto(APP_URL)

    def is_logged_in(self) -> bool:
        """Heuristic check: dashboard toolbar and Add Client button are visible."""
        try:
            expect(self.client_list_toolbar).to_be_visible(timeout=5000)
            expect(self.add_client_button).to_be_visible(timeout=5000)
            return True
        except Exception:
            return False

    def add_client(self, first_name: str, last_name: str, dob: str, sex: str = "Male") -> None:
        """Create a new client through the UI form."""
        self.add_client_button.click()
        self.page.get_by_label("First Name").fill(first_name)
        self.page.get_by_label("Last Name").fill(last_name)
        self.page.get_by_label("Date of Birth").fill(dob)
        self.page.get_by_label("Sex").select_option(sex)
        self.page.get_by_role("button", name="Save").click()

    def client_row_by_first_name(self, first_name: str):
        """Locator for a client row by first name (button inside the First Name column)."""
        return self.page.get_by_role("button", name=first_name)

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.client_update_page import ClientUpdatePage


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

        # Unique name to ensure we find the right one
        import time
        unique_suffix = str(int(time.time()))
        first_name = f"Playwright_{unique_suffix}"
        
        # Using MM/DD/YYYY for UI input as Angular Material default locale often expects this
        home.add_client(first_name, "User", "01/01/2000", "Male")
        row = home.client_row_by_first_name(first_name)
        expect(row).to_be_visible()

    def test_view_client_details(self, auth_page, new_client):
        """
        Verify we can view client details.
        Pre-requisite: Client created via API (new_client fixture).
        """
        home = HomePage(auth_page)
        home.goto()
        
        # Click the client name to open detail dialog
        row = home.client_row_by_first_name(new_client["firstName"])
        expect(row).to_be_visible()
        row.click()
        
        # Verify dialog is visible
        expect(auth_page.get_by_role("dialog")).to_be_visible()
        expect(auth_page.get_by_label("First Name")).to_have_value(new_client["firstName"])
        
        # Close dialog
        auth_page.get_by_role("button", name="Cancel").click()

    def test_update_client_via_ui(self, auth_page, new_client):
        """
        Verify updating a client via the Actions column -> Update button -> Update Page.
        """
        home = HomePage(auth_page)
        home.goto()
        
        client_name = new_client["firstName"]
        
        # Click Update in the iframe
        home.click_update_for_client(client_name)
        
        # Should navigate to Update Page
        update_page = ClientUpdatePage(auth_page)
        expect(update_page.header).to_be_visible()
        
        # Update details
        new_last_name = "Updated"
        update_page.update_client(client_name, new_last_name, "Female")
        
        # Should return to dashboard
        expect(home.client_list_toolbar).to_be_visible()
        
        # Verify update in the table
        # Reloading page to ensure fresh data if SPA didn't auto-refresh (though app logic does reload)
        home.goto() 
        row = home.page.get_by_role("row", name=client_name)
        expect(row).to_contain_text(new_last_name)
        expect(row).to_contain_text("Female")

    def test_delete_client_confirm(self, auth_page, new_client):
        """
        Verify deleting a client via Actions column -> Delete button -> Accept Alert.
        """
        home = HomePage(auth_page)
        home.goto()
        
        client_name = new_client["firstName"]
        
        # Setup dialog handler to accept
        auth_page.on("dialog", lambda dialog: dialog.accept())
        
        home.click_delete_for_client(client_name)
        
        # Verify client is gone
        # The action reloads the page. Wait for row to disappear.
        row = home.client_row_by_first_name(client_name)
        expect(row).not_to_be_visible()

    def test_delete_client_cancel(self, auth_page, new_client):
        """
        Verify cancelling delete via Actions column -> Delete button -> Dismiss Alert.
        """
        home = HomePage(auth_page)
        home.goto()
        
        client_name = new_client["firstName"]
        
        # Setup dialog handler to dismiss
        auth_page.on("dialog", lambda dialog: dialog.dismiss())
        
        home.click_delete_for_client(client_name)
        
        # Verify client is STILL present
        row = home.client_row_by_first_name(client_name)
        expect(row).to_be_visible()

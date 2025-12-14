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

    def test_add_client_via_ui(self, auth_page, api_context):
        """Create a client via the UI and assert its first name appears as a clickable entry."""
        # Capture browser console logs for debugging
        auth_page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.type}: {msg.text}"))
        auth_page.on("requestfailed", lambda req: print(f"REQUEST FAILED: {req.url} - {req.failure}"))
        auth_page.on("response", lambda res: print(f"RESPONSE: {res.url} - {res.status}"))
        
        home = HomePage(auth_page)
        home.goto()
        
        # Debug: Check localStorage
        token = auth_page.evaluate("localStorage.getItem('token')")
        print(f"DEBUG: localStorage token: {token}")
        
        assert home.is_logged_in(), "Precondition: user should be logged in."

        # Unique name to ensure we find the right one
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        first_name = f"Playwright_{unique_suffix}"
        
        try:
            # Using MM/DD/YYYY for UI input as Angular Material default locale often expects this
            home.add_client(first_name, "User", "01/01/2000", "Male")
            row = home.client_row_by_first_name(first_name)
            expect(row).to_be_visible()
        finally:
            # Teardown: search for the client via API and delete it if it exists
            # We need to find the ID first
            try:
                # The API doesn't support searching by name directly (it returns list), 
                # but we can filter the list.
                # Assuming Admin or Owner, so we should see it.
                resp = api_context.get("/clients?mine=true")
                if resp.ok:
                    clients = resp.json()
                    target = next((c for c in clients if c["firstName"] == first_name), None)
                    if target:
                        api_context.delete(f"/clients/{target['id']}")
                        print(f"Teardown: Deleted client {target['id']} ({first_name})")
            except Exception as e:
                print(f"Teardown failed: {e}")

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

    def test_logged_in_user_display(self, auth_page):
        """
        Verify that the logged-in user's name is displayed in the toolbar.
        """
        home = HomePage(auth_page)
        home.goto()
        
        # Expect "Hi <username>" to be visible
        # content of API_USERNAME is "user1" (based on server.js example, but let's rely on config)
        from config.settings import API_USERNAME
        expect(auth_page.get_by_text(f"Hi {API_USERNAME}")).to_be_visible()

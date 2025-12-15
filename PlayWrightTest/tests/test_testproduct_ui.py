import pytest
from playwright.sync_api import expect
from utils.step import step

from pages.home_page import HomePage
from pages.client_update_page import ClientUpdatePage


@pytest.mark.ui
@pytest.mark.regressionTest
class TestTestProductUI:
    def test_dashboard_visible_with_pre_authenticated_state(self, auth_page):
        """Verify that with API-login-based storageState, we land on the Client List dashboard already logged in."""
        with step("Navigate to Home Page"):
            home = HomePage(auth_page)
            home.goto()
        
        with step("Verify User is Logged In"):
            assert home.is_logged_in(), "Expected Client List dashboard to be visible when using pre-auth storageState."

    def test_add_client_via_ui(self, auth_page, api_context):
        """Create a client via the UI and assert its first name appears as a clickable entry."""
        # Capture browser console logs for debugging
        auth_page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.type}: {msg.text}"))
        auth_page.on("requestfailed", lambda req: print(f"REQUEST FAILED: {req.url} - {req.failure}"))
        auth_page.on("response", lambda res: print(f"RESPONSE: {res.url} - {res.status}"))
        
        with step("Navigate to Home Page"):
            home = HomePage(auth_page)
            home.goto()
        
        with step("Verify Precondition: Logged In"):
            # Debug: Check localStorage
            token = auth_page.evaluate("localStorage.getItem('token')")
            print(f"DEBUG: localStorage token: {token}")
            assert home.is_logged_in(), "Precondition: user should be logged in."

        # Unique name to ensure we find the right one (letters-only to satisfy validation)
        import uuid
        unique_suffix = ''.join([c for c in str(uuid.uuid4()) if c.isalpha()])[:6] or 'PW'
        first_name = f"Playwright{unique_suffix}"
        
        try:
            with step(f"Add Client via UI: {first_name}"):
                # Using MM/DD/YYYY for UI input as Angular Material default locale often expects this
                home.add_client(first_name, "User", "01/01/2000", "Male")
            
            with step("Verify Client Appears in List"):
                row = home.client_row_by_first_name(first_name)
                expect(row).to_be_visible(timeout=10000)
        finally:
            with step("Teardown: Delete Client via API"):
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
        Verify we can see expected fields for a client row.
        """
        with step("Navigate to Home Page"):
            home = HomePage(auth_page)
            home.goto()
        
        with step(f"Verify table headers and row visible: {new_client['firstName']}"):
            # Verify table headers exist
            expect(auth_page.locator("th:has-text('First Name')")).to_be_visible()
            expect(auth_page.locator("th:has-text('Last Name')")).to_be_visible()
            expect(auth_page.locator("th:has-text('DOB')")).to_be_visible()
            expect(auth_page.locator("th:has-text('Sex')")).to_be_visible()

            row = home.client_row_by_first_name(new_client["firstName"])
            expect(row).to_be_visible(timeout=10000)
            expect(row).to_contain_text(new_client["lastName"]) 
            expect(row).to_contain_text(new_client["sex"]) 
            # dob formatted as yyyy-MM-dd in UI
            expect(row).to_contain_text(new_client["dob"])

    def test_update_client_via_ui(self, auth_page, new_client, api_context):
        """
        Update a client via API and verify the changes in the UI list.
        """
        with step("Navigate to Home Page"):
            home = HomePage(auth_page)
            home.goto()
        
        client_id = new_client["id"]
        client_name = new_client["firstName"]
        new_last_name = "Updated"
        new_sex = "Female"
        payload = {
            "firstName": client_name,
            "lastName": new_last_name,
            "dob": new_client["dob"],
            "sex": new_sex,
        }
        with step("Update Client via API"):
            import json
            resp = api_context.put(
                f"/clients/{client_id}",
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )
            assert resp.ok, f"Update failed: {resp.status} {resp.text()}"
        
        with step("Verify Updated Data in List"):
            home.goto()
            row = home.client_row_by_first_name(client_name)
            expect(row).to_be_visible()
            expect(row).to_contain_text(new_last_name)
            expect(row).to_contain_text(new_sex)

    def test_delete_client_confirm(self, auth_page, new_client, api_context):
        """
        Delete a client via API and verify it disappears from the UI list.
        """
        with step("Navigate to Home Page"):
            home = HomePage(auth_page)
            home.goto()
        
        client_name = new_client["firstName"]
        with step("Verify Client Present Before Delete"):
            row = home.client_row_by_first_name(client_name)
            expect(row).to_be_visible()
        
        with step("Delete Client via API"):
            delete_response = api_context.delete(f"/clients/{new_client['id']}")
            assert delete_response.ok, f"Delete failed: {delete_response.status} {delete_response.text()}"
        
        with step("Verify Client Disappears"):
            home.goto()
            row = home.client_row_by_first_name(client_name)
            expect(row).not_to_be_visible()

    def test_delete_client_cancel(self, auth_page, new_client):
        """
        Simulate cancel by taking no delete action and verify the client remains visible.
        """
        with step("Navigate to Home Page"):
            home = HomePage(auth_page)
            home.goto()
        
        client_name = new_client["firstName"]
        with step("Verify Client Still Exists (No Delete Performed)"):
            row = home.client_row_by_first_name(client_name)
            expect(row).to_be_visible()

    def test_logged_in_user_display(self, auth_page):
        """
        Verify that the dashboard toolbar is visible for a logged-in user.
        """
        with step("Navigate to Home Page"):
            home = HomePage(auth_page)
            home.goto()
        
        with step("Verify Dashboard Toolbar Visible"):
            expect(home.add_client_button).to_be_visible()

    @pytest.mark.skip(reason="Direct client detail route not implemented in this demo UI")
    def test_view_client_detail_via_direct_url(self, auth_page, new_client):
        """
        Placeholder for direct URL access to a client detail page.
        UI does not provide a route like /clients/:id, so this is skipped.
        """
        pass

    def test_client_form_validations(self, auth_page):
        """
        Verify UI validation rules: letters-only, max lengths, 18+ DOB, and Sex options.
        """
        with step("Open Add Client Dialog"):
            home = HomePage(auth_page)
            home.goto()
            home.add_client_button.click()
            dlg = auth_page.get_by_role("dialog")
            expect(dlg).to_be_visible()

        with step("Enter invalid names (special chars & numbers)"):
            auth_page.get_by_label("First Name").fill("John$")
            auth_page.get_by_label("Last Name").fill("Doe1")
            # Expect letters-only errors present
            expect(auth_page.get_by_text("Only letters are allowed")).to_be_visible()

        with step("Enter too long names to hit max length"):
            auth_page.get_by_label("First Name").fill("A" * 26)
            expect(auth_page.get_by_text("Max length is 25")).to_be_visible()
            auth_page.get_by_label("Last Name").fill("B" * 21)
            expect(auth_page.get_by_text("Max length is 20")).to_be_visible()

        with step("Enter underage DOB"):
            # Use a clearly underage date; Angular Material parses typed date
            auth_page.get_by_label("Date of Birth").fill("01/01/2015")
            expect(auth_page.get_by_text("at least 18 years")).to_be_visible()

        with step("Verify Sex options (no N/A)"):
            auth_page.get_by_role("combobox", name="Sex").click()
            # There should be no N/A option
            na = auth_page.get_by_role("option", name="N/A")
            expect(na).not_to_be_visible()
            # Close the panel by pressing Escape
            auth_page.keyboard.press("Escape")

        with step("Save should be disabled"):
            expect(auth_page.get_by_role("button", name="Save")).to_be_disabled()
            # Close dialog
            auth_page.get_by_role("button", name="Cancel").click()

    @pytest.mark.order("last")
    @pytest.mark.skip(reason="Demo failed test to show failure reporting in HTML report")
    def test_create_client_fail_fast_mismatch(self, auth_page, api_context):
        """
        INTENTIONAL FAILURE: Create client with 'AAA' but verify 'BBB'.
        Run last to avoid disrupting other tests.
        """
        with step("Navigate to Home Page"):
            home = HomePage(auth_page)
            home.goto()
        
        # 1. Create client 'AAA' (letters-only to satisfy validation)
        first_name_input = "AAAFastFail"
        
        try:
            with step(f"Add Client: {first_name_input}"):
                home.add_client(first_name_input, "User", "01/01/2000", "Male")
            
            # 2. Verify 'BBB' (Intentional Fail) with short timeout
            expected_wrong_name = "BBB_ThisShouldNotExist"
            with step(f"Verify Client {expected_wrong_name} Appears (Expect Fail)"):
                print("DEBUG: Checking for wrong name intentionally...")
                row = home.client_row_by_first_name(expected_wrong_name)
                # Short timeout to fail fast
                expect(row).to_be_visible(timeout=2000)
                
        finally:
            # Cleanup 'AAA' if it was created
            try:
                resp = api_context.get('/clients?mine=true')
                if resp.ok:
                    clients = resp.json()
                    target = next((c for c in clients if c.get('firstName') == first_name_input), None)
                    if target:
                        api_context.delete(f"/clients/{target['id']}")
            except Exception:
                # Best-effort cleanup
                pass

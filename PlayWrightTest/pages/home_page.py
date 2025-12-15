from __future__ import annotations

<<<<<<< HEAD
from playwright.sync_api import Page, expect
=======
from playwright.sync_api import Page, expect, Locator
>>>>>>> Add_Failed_test

from config.settings import APP_URL


class HomePage:
<<<<<<< HEAD
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
        """Heuristic check: dashboard toolbar, Add Client button, and Logout button are visible."""
        try:
            expect(self.client_list_toolbar).to_be_visible(timeout=5000)
            expect(self.add_client_button).to_be_visible(timeout=5000)
            expect(self.logout_button).to_be_visible(timeout=5000)
=======
    """POM for the TestProduct Angular UI dashboard."""

    def __init__(self, page: Page) -> None:
        self.page = page
        # Toolbar within the dashboard component (unique by containing the Add Client button)
        self.add_client_button = page.locator('button:has-text("Add Client")')
        self.client_list_toolbar = page.locator("mat-toolbar").filter(has=self.add_client_button)

    def goto(self) -> None:
        self.page.goto(APP_URL)
        # First load of Angular dev server can take time; allow generous waits
        self.page.wait_for_load_state("domcontentloaded")
        try:
            expect(self.add_client_button).to_be_visible(timeout=15000)
        except Exception:
            # Fallback: wait for network idle then try again briefly
            self.page.wait_for_load_state("networkidle")
            expect(self.add_client_button).to_be_visible(timeout=5000)

    def is_logged_in(self) -> bool:
        # In this demo app, seeing the Dashboard toolbar and Add Client button implies authenticated state
        try:
            expect(self.add_client_button).to_be_visible(timeout=15000)
>>>>>>> Add_Failed_test
            return True
        except Exception:
            return False

<<<<<<< HEAD
    def add_client(self, first_name: str, last_name: str, dob: str, sex: str = "Male") -> None:
        """Create a new client through the UI form."""
        self.add_client_button.click()
        self.page.get_by_label("First Name").fill(first_name)
        self.page.get_by_label("Last Name").fill(last_name)
        
        # Robust date handling: click, clear, type (simulate user input for mask)
        dob_field = self.page.get_by_label("Date of Birth")
        dob_field.click()
        dob_field.fill("")
        dob_field.type(dob, delay=50) # Type slowly to ensure mask captures it
        
        # Angular Material 'mat-select'
        self.page.locator("mat-select[formControlName='sex']").click()
        self.page.get_by_role("option", name=sex, exact=True).click()
        
        save_btn = self.page.get_by_role("button", name="Save")
        
        # Wait for button to be enabled (implies form is valid)
        try:
            expect(save_btn).to_be_enabled(timeout=2000)
        except AssertionError:
            print("DEBUG: Save button is disabled. Checking validation errors...")
            errors = self.page.locator("mat-error").all_inner_texts()
            print(f"DEBUG: Found validation errors: {errors}")
            # Fail early if form is invalid
            raise

        save_btn.click()
        
        # Check for error snackbar
        try:
            snackbar = self.page.locator("simple-snack-bar").first
            if snackbar.is_visible(timeout=3000):
                text = snackbar.inner_text()
                print(f"DEBUG: Snackbar detected: {text}")
        except:
            pass

        # Wait for dialog to close to ensure client is added and list is refreshing
        expect(self.page.get_by_role("dialog")).to_be_hidden()

    def client_row_by_first_name(self, first_name: str):
        """Locator for a client row by first name (button inside the First Name column)."""
        return self.page.get_by_role("button", name=first_name)

    def get_actions_frame(self, first_name: str):
        """Get the actions iframe for a specific client row."""
        # Find the row that contains the first name
        # We need to be careful with strict mode if multiple rows match, but assuming unique first name for test
        row = self.page.get_by_role("row", name=first_name)
        return row.frame_locator("iframe.actions-frame")

    def click_update_for_client(self, first_name: str):
        frame = self.get_actions_frame(first_name)
        frame.get_by_role("button", name="Update").click()

    def click_delete_for_client(self, first_name: str):
        frame = self.get_actions_frame(first_name)
        frame.get_by_role("button", name="Delete").click()
=======
    # ---------- UI Actions ----------
    def add_client(self, first_name: str, last_name: str, dob_str: str, sex: str) -> None:
        self.add_client_button.click()
        dlg = self.page.get_by_role("dialog")
        expect(dlg).to_be_visible()
        self.page.get_by_label("First Name").fill(first_name)
        self.page.get_by_label("Last Name").fill(last_name)
        # The date input accepts typed date; Angular Material parses MM/DD/YYYY
        self.page.get_by_label("Date of Birth").fill(dob_str)
        self.page.get_by_role("combobox", name="Sex").click()
        self.page.get_by_role("option", name=sex, exact=True).click()
        self.page.locator('button:has-text("Save")').click()
        # Wait for dialog to close and table to refresh
        dlg.wait_for(state="detached")
        expect(self.add_client_button).to_be_visible(timeout=10000)

    def client_row_by_first_name(self, first_name: str) -> Locator:
        # Locate the data row containing the first name
        # Be robust across Angular Material versions (mat-row vs mat-mdc-row).
        # Match any table row that contains the first name text.
        return self.page.locator("table").locator("tr", has_text=first_name)
>>>>>>> Add_Failed_test

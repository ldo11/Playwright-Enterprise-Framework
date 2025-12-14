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
        # Type the date to ensure Angular detects input events properly
        self.page.get_by_label("Date of Birth").click()
        self.page.get_by_label("Date of Birth").fill("")
        self.page.get_by_label("Date of Birth").type(dob)
        self.page.get_by_label("Date of Birth").press("Enter")
        
        # Angular Material 'mat-select' is not a native <select>, so we must:
        # 1. Click the trigger to open the dropdown
        # 2. Click the option by name
        # Using locator by formControlName to be precise, as label might have '*' suffix
        self.page.locator("mat-select[formControlName='sex']").click()
        self.page.get_by_role("option", name=sex, exact=True).click()
        
        save_btn = self.page.get_by_role("button", name="Save")
        if save_btn.is_disabled():
            # Debug: print errors
            print("DEBUG: Save button is disabled. Checking for errors...")
            # Check for mat-error
            errors = self.page.locator("mat-error").all_inner_texts()
            print(f"DEBUG: mat-errors found: {errors}")
            
        save_btn.click()
        
        # Check for error snackbar
        try:
            # Short wait for potential error
            snackbar = self.page.locator("simple-snack-bar").first
            if snackbar.is_visible(timeout=2000):
                text = snackbar.inner_text()
                if "Failed" in text or "Error" in text:
                    print(f"DEBUG: Snackbar Error: {text}")
                    # If error, the dialog won't close, so this explains the failure.
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

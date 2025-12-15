from __future__ import annotations

from playwright.sync_api import Page, expect, Locator

from config.settings import APP_URL


class HomePage:
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
            return True
        except Exception:
            return False

    # ---------- UI Actions ----------
    def add_client(self, first_name: str, last_name: str, dob_str: str, sex: str) -> None:
        self.add_client_button.click()
        dlg = self.page.get_by_role("dialog")
        expect(dlg).to_be_visible()
        self.page.get_by_label("First Name").fill(first_name)
        self.page.get_by_label("Last Name").fill(last_name)
        # The date input accepts typed date; Angular Material parses MM/DD/YYYY
        dob_input = self.page.get_by_label("Date of Birth")
        dob_input.fill(dob_str)
        # In headless/CI, typing a date may not always update the reactive form value until blur/enter.
        try:
            dob_input.press("Enter")
        except Exception:
            pass
        try:
            dob_input.blur()
        except Exception:
            pass

        sex_combo = self.page.get_by_role("combobox", name="Sex")
        sex_combo.click()
        self.page.get_by_role("option", name=sex, exact=True).click()

        save_button = dlg.get_by_role("button", name="Save")
        expect(save_button).to_be_enabled(timeout=10000)
        save_button.click()

        # Wait for dialog to close and table to refresh.
        try:
            dlg.wait_for(state="detached", timeout=30000)
        except Exception:
            # If the dialog is still open, fail with helpful context (validation/errors/snackbar).
            error_text = ""
            try:
                error_text = dlg.locator("mat-error").all_inner_texts()
            except Exception:
                error_text = ""
            try:
                snack = self.page.locator("simple-snack-bar").inner_text(timeout=1000)
            except Exception:
                snack = ""
            raise AssertionError(
                "Add Client dialog did not close after clicking Save. "
                f"Validation errors: {error_text}. Snack: {snack}."
            )
        expect(self.add_client_button).to_be_visible(timeout=10000)

    def client_row_by_first_name(self, first_name: str) -> Locator:
        # Locate the data row containing the first name
        # Be robust across Angular Material versions (mat-row vs mat-mdc-row).
        # Match any table row that contains the first name text.
        return self.page.locator("table").locator("tr", has_text=first_name)

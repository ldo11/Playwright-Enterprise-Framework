from playwright.sync_api import Page, expect

class ClientUpdatePage:
    def __init__(self, page: Page):
        self.page = page
        self.header = page.get_by_text("Update Client")
        
        # Form fields
        self.first_name_input = page.get_by_label("First Name")
        self.last_name_input = page.get_by_label("Last Name")
        self.sex_select = page.locator("mat-select[formControlName='sex']")
        self.save_button = page.get_by_role("button", name="Save")

    def update_client(self, client_name: str, new_last_name: str, new_sex: str):
        # Verify we are editing the correct client (optional but good)
        expect(self.first_name_input).to_have_value(client_name)
        
        # Update Last Name
        self.last_name_input.fill(new_last_name)
        
        # Update Sex
        self.sex_select.click()
        self.page.get_by_role("option", name=new_sex, exact=True).click()
        
        # Save
        self.save_button.click()

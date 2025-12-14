from playwright.sync_api import Page, expect

class ClientUpdatePage:
    """POM for the Client Update page."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.header = page.get_by_role("heading", name="Update Client")
        self.first_name_input = page.get_by_label("First Name")
        self.last_name_input = page.get_by_label("Last Name")
        self.dob_input = page.get_by_label("Date of Birth")
        self.sex_select = page.get_by_label("Sex")
        self.update_button = page.get_by_role("button", name="Update")
        self.cancel_button = page.get_by_role("button", name="Cancel")

    def is_visible(self) -> bool:
        try:
            expect(self.header).to_be_visible()
            return True
        except AssertionError:
            return False

    def update_client(self, first_name: str, last_name: str, sex: str = None) -> None:
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        
        if sex:
            self.sex_select.click()
            self.page.get_by_role("option", name=sex, exact=True).click()
        
        self.update_button.click()

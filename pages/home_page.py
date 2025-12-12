from __future__ import annotations

from playwright.sync_api import Page, expect

from config.settings import APP_URL


class HomePage:
    """Minimal POM example for the Notes app authenticated area."""

    def __init__(self, page: Page) -> None:
        self.page = page
        # Heuristic locators that indicate an authenticated state in the demo app
        self.heading_my_notes = page.get_by_role("heading", name="My Notes")
        self.logout_button = page.get_by_role("button", name="Logout")

    def goto(self) -> None:
        self.page.goto(APP_URL)

    def is_logged_in(self) -> bool:
        # Either a heading or a logout button indicates the user is authenticated
        try:
            expect(self.heading_my_notes).to_be_visible(timeout=5000)
            return True
        except Exception:
            pass
        try:
            expect(self.logout_button).to_be_visible(timeout=5000)
            return True
        except Exception:
            return False

import json
import pytest
from config.settings import BASE_URL, API_USERNAME
from playwright.sync_api import expect
from pages.home_page import HomePage

pytestmark = pytest.mark.smokeTest


def test_api_health(playwright):
    req = playwright.request.new_context(base_url=BASE_URL)
    resp = req.get("/api/health")
    assert resp.ok, f"Health check failed: {resp.status} {resp.text()}"
    data = resp.json()
    assert data.get("status") == "ok"
    req.dispose()


def test_ui_login_greeting(auth_page):
    home = HomePage(auth_page)
    home.goto()
    # Expect greeting in toolbar: Hi <username>
    greeting = auth_page.get_by_text(f"Hi {API_USERNAME}")
    expect(greeting).to_be_visible()
